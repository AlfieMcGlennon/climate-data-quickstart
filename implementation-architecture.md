# Climate Data Toolkit: Implementation Architecture

> **Historical document.** Written during initial project planning
> (2026-04-19). The agent definitions and pipeline skill described here
> were implemented and used to build the first 12 datasets. The actual
> agent files at `.claude/agents/` and `.claude/skills/` are the
> authoritative versions. For current project state, see
> `SESSION_HANDOFF.md` and `PLAN.md`.

---

## 1. CLAUDE.md (Root of Repo)

```markdown
# Climate Data Toolkit

## Project Purpose
A curated, practical reference repository for climate and weather datasets.
Every output must be useful to a researcher who has never used the dataset before.
The audience is MSc/PhD students, early-career climate scientists, and climate risk analysts.

## Style Rules
- No em dashes anywhere. Use hyphens, commas, or restructure the sentence.
- No emojis anywhere.
- No flowery language. Direct, technical, human.
- British English spelling throughout (colour, analyse, centre, licence).
- Code comments explain WHY, not WHAT.
- Variable names in docs must match the exact API variable name. No paraphrasing.
- Headings use sentence case, not title case.
- Every factual claim about a dataset must be traceable to a primary source.
- Do not say "comprehensive" or "robust" or "leveraging" or "utilize".

## Source Rules
1. PRIMARY ONLY for technical specs: official dataset documentation pages
2. SECONDARY for context: peer-reviewed papers describing the dataset
3. NEVER trust your training data for variable names, API parameters, or URLs
4. If you cannot verify something against a live primary source, mark it [VERIFY]
5. When scanning other repos for ideas, note strengths/weaknesses in a comment block
   but never copy structure, text, or code patterns

## File Naming
- Docs: docs/{dataset-slug}/README.md, docs/{dataset-slug}/variables.md
- Scripts: scripts/{dataset_slug}_download.py
- Notebooks: notebooks/{dataset_slug}_quickstart.ipynb
- Research briefs: .research/{dataset_slug}_brief.md (gitignored)
- Test logs: .test_logs/{dataset_slug}.log (gitignored)

## Config Block Standard
Every download script and notebook begins with:
```python
# ==================================================================
# USER CONFIGURATION - Edit these values for your use case
# ==================================================================
VARIABLES = ["2m_temperature"]
YEAR = 2023
MONTHS = [7]
BBOX = {"north": 55, "south": 49, "west": -8, "east": 2}  # UK
OUTPUT_DIR = "./data"
# ==================================================================
```

## API Key Handling
- Keys live in standard config files (~/.cdsapirc, ~/.netrc)
- Scripts reference keys via standard library mechanisms (cdsapi.Client() reads ~/.cdsapirc)
- NEVER print, log, or commit keys
- Scripts must check for key existence and fail with a clear message if missing
- .gitignore excludes: .cdsapirc, .netrc, *.key, data/, .research/, .test_logs/

## Notebook Standards
- Every notebook must be runnable top-to-bottom without modification after setting config
- First cell: config block
- Second cell: imports with version check
- Third cell: download (small test pull, 1 day, 1 variable, small region)
- Fourth cell: open with xarray, print dataset summary
- Fifth cell: basic plot (map or time series, whichever fits)
- Sixth cell: "next steps" markdown cell pointing to full docs

## Python Standards
- Type hints on all function signatures
- Docstrings on all functions (Google style)
- No wildcard imports
- Requirements: cdsapi, xarray, netcdf4, matplotlib, cartopy, numpy, pandas
- Target Python 3.10+

## Agent Workflow
This project uses a three-stage pipeline per dataset:
1. Research subagent gathers specs from primary sources -> writes brief to .research/
2. Main session writes docs + code using the brief
3. Test subagent validates code, Review subagent checks quality

See .claude/agents/ and .claude/skills/ for definitions.

IMPORTANT: When processing a dataset, always start by reading the research brief
from .research/{dataset_slug}_brief.md. Do not skip this step.
```

---

## 2. Agent Definitions

### .claude/agents/researcher.md

```markdown
---
name: researcher
description: Gathers technical specifications for a climate dataset from primary sources only
model: sonnet
effort: high
maxTurns: 20
disallowedTools: [Write, Edit]
---

You are a research agent for the climate-data-toolkit project.

Given a dataset name and its official documentation URL(s), your job is to
gather every technical specification needed to write documentation and code.

## What you must find

For every dataset, extract and return ALL of the following:

1. IDENTITY
   - Full official name
   - Abbreviation/acronym
   - Provider organisation
   - DOI (if available)
   - Official documentation URL (the one you actually read, not a guess)

2. SPATIAL SPECS
   - Grid type (regular lat/lon, reduced Gaussian, unstructured, station-based)
   - Resolution (in degrees and approximate km)
   - Coverage (global, regional, land-only, etc.)
   - Coordinate reference system if specified

3. TEMPORAL SPECS
   - Temporal resolution (hourly, 3-hourly, 6-hourly, daily, monthly, climatology)
   - Temporal coverage (start year to present, or fixed range)
   - Update frequency (real-time, monthly, annual, static)
   - Any known latency (e.g., "available 3 months behind real-time")

4. VARIABLES
   - List ALL available variables with their exact API/short names
   - For the top 10 most commonly used, include: long name, units, description
   - Note any variable naming quirks (e.g., ERA5 uses "2t" in GRIB but
     "2m_temperature" in the CDS API)

5. ACCESS METHOD
   - Exact API endpoint or download mechanism
   - Required authentication (API key, account registration, etc.)
   - Python package needed (cdsapi, requests, wget, etc.)
   - Example API call from official docs (if available)
   - Any rate limits or queue behaviour
   - Available output formats (NetCDF, GRIB, CSV, etc.)

6. LICENCE
   - Exact licence name and link
   - Any attribution requirements
   - Commercial use restrictions (if any)

7. KNOWN ISSUES
   - Any documented data gaps, discontinuities, or biases
   - Any known processing artefacts
   - Any recent version changes users should know about

8. CITATION
   - Official citation string
   - Key reference paper (if any)

## Rules
- Fetch and read the actual documentation pages. Do not rely on training data.
- If a field cannot be determined from primary sources, write "[NOT FOUND IN DOCS]"
  rather than guessing.
- Return findings as structured markdown, nothing else.
- Do not write any files. Output to stdout only.
- For variable lists longer than 50, provide the full list but group by category.
```

### .claude/agents/tester.md

```markdown
---
name: tester
description: Validates download scripts and notebooks by running them with minimal parameters
model: sonnet
effort: high
maxTurns: 15
---

You are a test agent for the climate-data-toolkit project.

Given a dataset slug, you validate that its download script and notebook work correctly.

## Test procedure

### 1. Pre-flight checks
- Verify the script file exists at scripts/{dataset_slug}_download.py
- Verify the notebook exists at notebooks/{dataset_slug}_quickstart.ipynb
- Verify required API credentials exist (check ~/.cdsapirc etc.)
- Verify required Python packages are installed

### 2. Script test
- Read the download script
- Identify the config block
- Modify ONLY the config block to use minimal parameters:
  - 1 day of data
  - 1 variable (the simplest/smallest one)
  - Smallest reasonable bounding box
- Run the script
- Check: did it produce an output file?
- Check: can xarray.open_dataset() read the file?
- Check: are the expected variables present?
- Check: are the dimensions reasonable (not empty, not enormous)?
- Log results to .test_logs/{dataset_slug}.log

### 3. Notebook test (lightweight)
- Convert notebook to script: jupyter nbconvert --to script
- Run the converted script
- Check for errors
- Log results

### 4. Error handling
- If the script fails, read the error carefully
- Common issues to fix:
  - Wrong variable name -> check against the research brief
  - Authentication error -> report, do not fix (user's key issue)
  - Timeout -> report as a queue time issue, not a bug
  - Import error -> add to requirements.txt
- Fix fixable issues and re-run (up to 3 attempts)
- After fixes, re-run from scratch to confirm clean execution

### 5. Output
Write a test report to .test_logs/{dataset_slug}.log:
```
Dataset: {name}
Date tested: {date}
Script: PASS/FAIL
Notebook: PASS/FAIL
Output file: {filename}, {size}
Variables found: {list}
Dimensions: {dict}
Issues found: {list or "None"}
Fixes applied: {list or "None"}
```
```

### .claude/agents/reviewer.md

```markdown
---
name: reviewer
description: Final quality review of docs, code, and consistency for a dataset entry
model: opus
effort: high
maxTurns: 10
disallowedTools: [Bash]
---

You are a quality reviewer for the climate-data-toolkit project.

Given a dataset slug, review ALL outputs for quality, accuracy, and consistency.

## Review checklist

### Documentation (docs/{dataset_slug}/README.md)
- [ ] All factual claims match the research brief in .research/
- [ ] No em dashes, no emojis, British English spelling
- [ ] Variable names match exact API names
- [ ] Resolution/coverage/temporal range are stated precisely
- [ ] Access instructions are step-by-step and complete
- [ ] Licence is stated with attribution requirements
- [ ] No "comprehensive", "robust", "leverage", "utilize"
- [ ] Reads like a human wrote it, not a language model

### Code (scripts/{dataset_slug}_download.py)
- [ ] Config block is at the top and clearly marked
- [ ] No hardcoded API keys or paths
- [ ] Graceful failure if credentials missing
- [ ] Type hints on functions
- [ ] Docstrings present
- [ ] Code matches what the docs describe
- [ ] Variable names in code match variable names in docs

### Notebook (notebooks/{dataset_slug}_quickstart.ipynb)
- [ ] Follows the 6-cell structure from CLAUDE.md
- [ ] Config block is first
- [ ] Imports include version checks
- [ ] Plot is sensible (correct units, labelled axes, colourbar if map)
- [ ] "Next steps" cell exists and points to docs

### Consistency
- [ ] Variable names are identical across docs, script, and notebook
- [ ] Resolution stated in docs matches what the code requests
- [ ] Any [VERIFY] tags have been addressed or flagged for human review

### Test results
- [ ] Read .test_logs/{dataset_slug}.log
- [ ] All tests passed, or failures are documented with explanations

## Output
Write a review report to .review/{dataset_slug}_review.md:

```
# Review: {dataset name}
Date: {date}
Reviewer: claude-reviewer-agent

## Score: {X}/10

## Issues found:
1. {issue + location + severity}

## Suggestions:
1. {suggestion}

## Human attention needed:
1. {any [VERIFY] tags or judgment calls}
```

Score guide:
- 9-10: Ship it. Minor formatting tweaks at most.
- 7-8: Good but has factual or consistency issues to fix.
- 5-6: Significant rework needed.
- Below 5: Restart from research phase.
```

---

## 3. Custom Skills

### .claude/skills/dataset-pipeline/SKILL.md

```markdown
---
name: dataset-pipeline
description: Orchestrates the full research-write-test-review pipeline for a single dataset
---

# Dataset Pipeline Skill

## Trigger
When asked to "process", "document", or "add" a dataset to the toolkit.

## Full pipeline

### Step 1: Research
Invoke the researcher agent with the dataset name and official URL.
Save output to .research/{dataset_slug}_brief.md

### Step 2: Write documentation
Read the research brief.
Create docs/{dataset_slug}/README.md following CLAUDE.md template.
If the dataset has more than 10 variables, also create docs/{dataset_slug}/variables.md

### Step 3: Write code
Read the research brief AND the docs just written.
Create scripts/{dataset_slug}_download.py with standard config block.
Create notebooks/{dataset_slug}_quickstart.ipynb with 6-cell structure.

### Step 4: Test
Invoke the tester agent with the dataset slug.
Read the test log.
If tests failed with fixable issues, apply fixes and re-invoke tester.
Maximum 3 test-fix cycles.

### Step 5: Review
Invoke the reviewer agent with the dataset slug.
Read the review report.
If score is below 7, apply suggested fixes and re-invoke reviewer.
Maximum 2 review cycles.

### Step 6: Summary
Print a one-line summary: dataset name, test result, review score, any [VERIFY] flags remaining.
```

### .claude/skills/config-validator/SKILL.md

```markdown
---
name: config-validator
description: Validates that config blocks in scripts and notebooks follow the project standard
---

# Config Validator Skill

## Trigger
After writing or editing any download script or notebook.

## Checks
1. Config block exists and is clearly delimited with comment markers
2. No hardcoded paths outside config block
3. No API keys or credentials in the file
4. Config values are sensible defaults (not empty, not absurdly large)
5. BBOX values make geographic sense (north > south, reasonable lon range)
6. Output directory uses relative path, not absolute
```

---

## 4. Pipeline Execution

### Option A: Interactive (recommended for first run)

```bash
# From the repo root, in Claude Code:

# First, scaffold the repo structure
mkdir -p docs scripts notebooks common examples .research .test_logs .review

# Process your template dataset first (ERA5 single levels)
# Do this interactively so you can steer the output and set the quality bar

claude
> /dataset-pipeline era5-single-levels https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels

# Review the output manually
# This becomes your golden reference that all other datasets are measured against

# Once you're happy with the template, run the rest headless
```

### Option B: Headless batch (after template is set)

```bash
#!/bin/bash
# pipeline.sh - Run from repo root
# Requires: claude CLI, API key, CDS credentials

set -e

# Dataset slug : primary documentation URL
declare -A DATASETS=(
  ["era5-pressure-levels"]="https://cds.climate.copernicus.eu/datasets/reanalysis-era5-pressure-levels"
  ["era5-land"]="https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land"
  ["era5-daily-stats"]="https://cds.climate.copernicus.eu/datasets/derived-era5-single-levels-daily-statistics"
  ["hadcet"]="https://www.metoffice.gov.uk/hadobs/hadcet/"
  ["hadcrut5"]="https://www.metoffice.gov.uk/hadobs/hadcrut5/"
  ["cmip6"]="https://cds.climate.copernicus.eu/datasets/projections-cmip6"
  ["glofas"]="https://ewds.climate.copernicus.eu/datasets/cems-glofas-historical"
  ["ghcnd"]="https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily"
  ["gpw-population"]="https://www.earthdata.nasa.gov/data/projects/gpw"
  ["e-obs"]="https://cds.climate.copernicus.eu/datasets/insitu-gridded-observations-europe"
  ["ukcp18"]="https://catalogue.ceda.ac.uk/uuid/9842e395f2d04f48a177c3550756bf98/"
  ["chirps"]="https://www.chc.ucsb.edu/data/chirps"
)

mkdir -p .research .test_logs .review logs

for slug in "${!DATASETS[@]}"; do
  url="${DATASETS[$slug]}"
  echo "=========================================="
  echo "Processing: $slug"
  echo "Source: $url"
  echo "=========================================="

  claude -p \
    "Process the dataset '$slug' using the dataset-pipeline skill. \
     The primary documentation URL is: $url \
     Follow CLAUDE.md instructions exactly. \
     Use the researcher agent first, save brief to .research/${slug}_brief.md. \
     Then write docs, script, and notebook. \
     Then run the tester agent. \
     Then run the reviewer agent. \
     Print a final summary line." \
    --allowedTools "Read,Edit,Write,Bash(python*),Bash(jupyter*),Bash(pip*),Bash(cat*),Bash(ls*),Bash(mkdir*)" \
    > "logs/${slug}.log" 2>&1

  echo "Completed: $slug ($(date))"
  echo ""
  sleep 60  # Buffer between datasets to avoid rate limits
done

echo "=========================================="
echo "PIPELINE COMPLETE"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Review .review/ for quality scores"
echo "2. Search all files for [VERIFY] tags"
echo "3. Add your editorial one-liners to each docs/*/README.md"
echo "4. Run: grep -r '\[VERIFY\]' docs/ scripts/ notebooks/"
```

### Option C: Claude Cowork (no terminal)

If you want to use Cowork instead of Claude Code CLI:

1. Create a project folder on your desktop: `climate-data-toolkit/`
2. Drop the CLAUDE.md file in the root
3. Create the .claude/agents/ and .claude/skills/ folders with the files above
4. Open Cowork, point it at the folder
5. Say: "Process the ERA5 single levels dataset using the dataset-pipeline skill.
   The official docs are at https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels"
6. Let it run, review, then repeat for each dataset

The downside: Cowork can't run headless overnight. You'd need to babysit each one.
The upside: You can steer mid-task without terminal knowledge.

---

## 5. Post-Pipeline Human Pass

After all datasets are processed, your manual checklist:

```bash
# 1. Find everything that needs your attention
grep -rn "\[VERIFY\]" docs/ scripts/ notebooks/
grep -rn "\[SECONDARY SOURCE\]" docs/

# 2. Check review scores
cat .review/*_review.md | grep "Score:"

# 3. Add your editorial to each dataset README
# For each docs/*/README.md, add a section:

## When I reach for this
# Your 2-3 sentence opinion on when this dataset is the right choice
# vs alternatives. This is what makes the repo yours.

# 4. Write the root README.md
# Dataset overview table, installation, quickstart, your framing

# 5. Test the full flow on a clean machine (or ask a friend to clone and try)

# 6. Tag v0.1.0 and push
```

---

## 6. What You Actually Need to Learn

Honest assessment of skills you need that you might not have yet:

**Things you already know:**
- Python, xarray, matplotlib, cartopy
- ERA5, CDS API, HPC workflows
- Git, repo structure
- How these datasets actually work scientifically

**Things you need to pick up (small learning curve):**
- Claude Code agent/skill file format (YAML frontmatter + markdown, 30 mins to learn)
- The -p headless flag and --allowedTools syntax (read the docs page, 15 mins)
- How to write a good CLAUDE.md (the one above is your starting point)

**Things you do NOT need:**
- MCP servers (overkill for this project)
- The Antigravity skills library (1,234 skills you won't use)
- Complex hook systems
- Agent teams with tmux and git worktrees

Keep it simple. Three agents, one skill, one CLAUDE.md, one bash script.
The complexity should be in the content, not the tooling.
