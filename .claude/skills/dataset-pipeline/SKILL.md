---
name: dataset-pipeline
description: Orchestrates the full research-write-test-review pipeline for a single climate dataset. Use when asked to process, document, or add a dataset to the toolkit.
---

# Dataset pipeline skill

## Trigger

Use this skill when asked to "process", "document", "add", or "build" a dataset
in the climate-data-toolkit.

Invocation expects:
- `dataset_slug` (e.g., `era5-single-levels`)
- `dataset_name` (human-readable name)
- Primary documentation `url`
- Access pattern: `A` (CDS API), `B` (direct download), `C` (custom API),
  `D` (cloud Zarr), or `E` (EWDS API)

## Pre-flight

1. Read `CLAUDE.md` in the repo root.
2. Read `PLAN.md` to find this dataset's row in the table. Note access pattern,
   default region, credentials.
3. Check if `.research/{dataset_slug}_brief.md` already exists. If so, skip to
   step 2 (writing) and reuse the existing brief.
4. If the dataset is marked as blocked in `PLAN.md` (e.g., CEDA not ready for
   UKCP18), log the skip and exit. Do not fail the pipeline.

## Step 1: Research

Invoke the `researcher` agent with:
- Dataset name
- Official documentation URL
- Instruction to save brief to `.research/{dataset_slug}_brief.md`

If the researcher agent cannot write files itself, capture its output and save
it from the main session.

Validate the brief has all 8 sections populated. If any critical section is
missing (Identity, Access method, Variables), re-invoke the researcher with a
more specific prompt.

## Step 2: Write documentation

Read the research brief.

Create `docs/{dataset-slug}/README.md` with sections:
- What this dataset is (2-3 sentences from Identity section)
- Spatial and temporal coverage (from Spatial/Temporal specs)
- Variables (table for top 10, link to `variables.md` if more than 10)
- Access (step-by-step, pattern-specific instructions)
- Licence and attribution
- Citation
- Known issues (if any from brief)
- Further reading (brief's URL plus any papers)

If more than 10 variables, create `docs/{dataset-slug}/variables.md` with the
full grouped list.

Self-check before moving on:
- No em dashes
- No banned words (comprehensive, robust, leverage, utilize, seamless, powerful,
  cutting-edge, empower, unlock, dive into, delve into)
- British English spelling
- Variable names match brief exactly
- Licence section present

## Step 3: Write download script

Create `scripts/{dataset_slug_underscored}_download.py`:
- Config block at top, bounded by `# ==========` markers
- Sensible small defaults for test pulls
- Credential check call from `common.credentials` matching the access pattern
- Pattern-appropriate client setup (cdsapi.Client, requests.Session, etc.)
- `def download(...)` function with type hints and Google docstring
- `if __name__ == "__main__":` block calling download()
- Fail gracefully if credentials missing, pointing to registration URL

## Step 4: Write quickstart notebook

Create `notebooks/{dataset_slug_underscored}_quickstart.ipynb` with six cells:

1. **Code - config block** (same as script's config block, minus any constants
   that do not apply)
2. **Code - imports with version check** - `import xarray as xr; print(f"xarray {xr.__version__}")`
3. **Code - download call** - calls the download function from the script, or
   replicates the minimal pull inline
4. **Code - open and inspect** - `ds = xr.open_dataset(...); print(ds)`
5. **Code - plot** - one map or time series, labelled axes, units, colourbar
6. **Markdown - next steps** - pointer to `docs/{dataset-slug}/README.md`,
   suggested extensions

Build the `.ipynb` as JSON directly. Use `nbformat` version 4.

## Step 5: Test

Invoke the `tester` agent with the dataset slug.

Wait for completion. Read `.test_logs/{dataset_slug}.log`.

Possible outcomes:
- **PASS**: move on.
- **DEFERRED** (queue wait, transient network): move on, note in PLAN.md.
- **FAIL**: examine the error, apply fixes, re-invoke tester. Max 3 cycles.
  After 3 cycles, log failure, update PLAN.md status to "needs human review",
  commit what exists (docs and script), and exit this skill for this dataset.

## Step 6: Review

Invoke the `reviewer` agent with the dataset slug.

Wait for completion. Read `.review/{dataset_slug}_review.md`.

Possible outcomes:
- Score >= 7 and recommendation `SHIP`: move on.
- Score < 7 and recommendation `FIX_AND_RESUBMIT`: apply suggestions from the
  review, re-invoke reviewer. Max 2 cycles.
- Score < 5 and recommendation `RESTART`: log this as a quality failure,
  update PLAN.md status, move on without committing. Flag for human attention.
- After 2 fix cycles still below 7: commit with status "needs polish" note,
  update PLAN.md, move on.

## Step 7: Commit

Only commit if review score >= 7.

Stage:
- `docs/{dataset-slug}/`
- `scripts/{dataset_slug_underscored}_download.py`
- `notebooks/{dataset_slug_underscored}_quickstart.ipynb`
- `PLAN.md` (status update)

Commit message:
```
Add {dataset-slug}: {one-line description}

Review score: {X}/10
Test status: {PASS|DEFERRED}
{any [VERIFY] tag count}
```

Do not stage: `.research/`, `.test_logs/`, `.review/` (all gitignored).

## Step 8: Update PLAN.md

Mark the dataset row status:
- `shipped` (review >= 7, test passed)
- `needs polish` (review 5-6 but shipped)
- `needs human review` (review < 5 or test failed after retries)
- `skipped: {reason}` (blocked by credentials)

## Step 9: Summary

Print one line:
```
{dataset_slug}: {status} (test={PASS|FAIL|DEFERRED}, review={X}/10, verify_tags={n})
```

## Pipeline-level rules

- Never block on a single dataset. Always continue to the next on failure.
- Never commit `.research/`, `.test_logs/`, or `.review/` contents.
- Never print credentials in logs.
- British English throughout all generated content.
- On any step, if `CLAUDE.md` rules conflict with agent output, `CLAUDE.md` wins.
