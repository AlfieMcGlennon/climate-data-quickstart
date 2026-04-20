# Session handoff: climate-data-quickstart

Read this first if you are a new Claude Code session picking up work on
this repo. Written 2026-04-20. Supersedes `PLAN.md` for the current
state; `PLAN.md` is preserved as the original intent.

## One-line project summary

A curated, opinionated reference repo for twelve climate datasets (docs
+ download scripts + quickstart notebooks), plus a local-only Streamlit
desktop app that lets anyone select a dataset, fill in a form, and
download the data without writing Python.

## Who this is for

MSc/PhD climate students, early-career climate scientists, and climate
risk analysts. User (Alfie) is building it as a portfolio piece plus a
useful resource. British English throughout. See `CLAUDE.md` for the
full style and source rules.

## Current state (24 commits on `main`)

### What is shipped

- **12 datasets** each with `docs/{slug}/README.md`, `scripts/{slug}_download.py`,
  `notebooks/{slug}_quickstart.ipynb`. Two more (UKCP18, GPWv4) are
  deferred pending the user registering for CEDA and NASA Earthdata.
- **Streamlit local-only desktop app** at `app/` with:
  - Dataset picker + credential status sidebar
  - Shared form widgets (bbox presets, time pickers, output dir)
  - One `render_form()` module per dataset in `app/dataset_pages/`
  - Dispatcher (`app/runner.py`) calling the existing `scripts/*_download.download()` functions
  - Special EDH flow with streaming code snippet + optional file download
- **Setup / launch scripts**: `setup.bat`, `setup.sh`, `run_app.bat`, `run_app.sh`, `environment.yml`
- **Credentials helper** (`common/credentials.py` + `app/credentials.py`) that checks five patterns (CDS, EDH, NASA Earthdata, CEDA, EWDS) without ever reading the key strings themselves
- **Root `README.md`** with the "Two ways to use it" framing
- `LICENSE` (MIT)

### What is verified live

- HadCET parsers (monthly + daily, all four variants) against Met Office
- HadCRUT5 URL pattern + `tas_mean` variable name against Met Office
- GHCNd parser against Heathrow station (39,923 rows)
- Earth Data Hub Zarr URL against EDH catalogue (requires EDH credentials
  in `~/_netrc` on Windows)
- ERA5 single levels full download against CDS

### What is still to do (for v0.1 ship)

See "Open threads" section at the bottom.

## Repo layout

```
climate-data-quickstart/
|
|-- CLAUDE.md                  # Style rules + access patterns + notebook standard
|-- PLAN.md                    # Original plan, frozen in time
|-- SESSION_HANDOFF.md         # This file - current state for a new session
|-- README.md                  # Public repo README with "Two ways to use it"
|-- LICENSE                    # MIT
|-- requirements.txt
|-- environment.yml            # conda alternative
|-- setup.bat / setup.sh       # One-time venv + pip install
|-- run_app.bat / run_app.sh   # Launches Streamlit at localhost:8501
|
|-- app/                       # The Streamlit desktop app (NEW this session)
|   |-- main.py                # Entry point + sidebar router + result panel
|   |-- credentials.py         # UI-friendly status checks for 5 cred patterns
|   |-- forms.py               # Shared widgets: bbox, time, output, result panel
|   |-- runner.py              # Thin dispatcher to scripts/*_download
|   \-- dataset_pages/         # One module per dataset with render_form()
|       |-- __init__.py        # DATASETS registry (slug -> (name, module))
|       |-- era5_single_levels.py
|       |-- era5_pressure_levels.py
|       |-- era5_land.py
|       |-- era5_daily_stats.py
|       |-- earth_data_hub.py  # Has streaming_snippet() in addition to render_form()
|       |-- hadcet.py
|       |-- hadcrut5.py
|       |-- cmip6.py
|       |-- glofas.py
|       |-- ghcnd.py
|       |-- e_obs.py
|       \-- chirps.py
|
|-- common/
|   |-- __init__.py
|   |-- credentials.py         # Shared credential checks used by scripts
|   \-- plotting.py            # Plotting defaults (colourmaps, map axes)
|
|-- docs/                      # Per-dataset README + variables.md
|   |-- era5-single-levels/    # The heaviest entry, also the template
|   |-- era5-pressure-levels/
|   |-- era5-land/
|   |-- era5-daily-stats/
|   |-- earth-data-hub/
|   |-- hadcet/
|   |-- hadcrut5/
|   |-- cmip6/
|   |-- glofas/
|   |-- ghcnd/
|   |-- e-obs/
|   \-- chirps/
|
|-- notebooks/                 # Per-dataset quickstart .ipynb
|-- scripts/                   # Per-dataset download.py
|
|-- .claude/
|   |-- agents/                # researcher.md, tester.md, reviewer.md
|   |-- skills/dataset-pipeline/  # Orchestration skill
|   \-- settings.local.json    # Permissions allowlist for the project
|
\-- .gitignore                 # Python + credentials + data/ + .research/ etc.
```

## Running the app right now

There may already be a Streamlit process bound to port 8501 from the
previous session (background command `btvbgnsmo`). If so, the user can
refresh http://localhost:8501. If not:

```
cd C:\climate-data\climate-data-quickstart
.\run_app.bat
```

The app binds to `localhost` only. Credentials are read from the user's
`~/.cdsapirc`, `~/.netrc` or `~/_netrc` (Windows convention), or
environment variables. The app itself never sees or stores key strings.

## Architecture notes worth knowing

### Three credential patterns across 12 datasets

- **CDS API**: ERA5 family, CMIP6, E-OBS. Reads `~/.cdsapirc`.
- **Direct HTTP**: HadCET, HadCRUT5, GHCNd, CHIRPS. No auth.
- **Custom**: Earth Data Hub (via netrc), GloFAS (EWDS endpoint + env var),
  NASA Earthdata for GPWv4 (via netrc), CEDA for UKCP18 (bearer token).

See `common/credentials.py` for check functions and
`app/credentials.py` for the UI-friendly status panel that feeds the
sidebar.

### Scripts / notebooks / app are layered

```
app (Streamlit UI)  ->  scripts/*_download.download()  ->  cdsapi.Client() / requests
     ^
     |
notebooks/*.ipynb   (same download() functions, interactive)
```

The app is additive. Existing scripts and notebooks keep working
unchanged for CLI users.

### EDH is streaming, not queued

The Earth Data Hub page is the exception. Its primary output is a
streaming code snippet the user can copy, plus an optional "Download
sliced data to file" button. The page exposes both `render_form()` and
`streaming_snippet()`; `main.py` checks the slug and routes accordingly.

### The netrc platform gotcha

On Windows, File Explorer does not permit leading-dot filenames, so
users have `~/_netrc` instead of `~/.netrc`. Both `common/credentials.py`
and `app/credentials.py` check both locations. Do not assume one or the
other.

## Known working, known broken, known TBD

### Working (verified live by the user in this session)

- Streamlit app boots cleanly
- Dataset sidebar renders 12 items
- Credential status panel (CDS configured, EDH configured via _netrc)
- EDH "Show streaming code" button produces a correct code snippet
- EDH "Download sliced data to file" worked once the `ds.sizes` fix was
  applied to distinguish `valid_time` from `time`

### Not fully verified yet

- Other dataset forms (ERA5 single/pressure/land/daily stats, HadCET,
  HadCRUT5, CMIP6, GloFAS, GHCNd, E-OBS, CHIRPS) have been smoke-tested
  at import level but the user has not clicked through each to confirm
  the full flow end to end.

### Open threads

1. **Apply the `developing-with-streamlit` Claude Code skill.** The user
   installed it between sessions and wants the app/ code reviewed and
   polished against that skill's guidance. This is the first thing to do
   in the new session: load the skill, read it, audit `app/main.py`,
   `app/forms.py`, `app/dataset_pages/*.py`, and `app/credentials.py`
   against its patterns.
2. **Editorial "when I reach for this" lines** per dataset README. User
   wants one or two sentences in their own voice per docs/*/README.md so
   it reads as theirs, not as generated. Human touch - offer to help draft
   but user decides the voice.
3. **End-to-end smoke test** on a clean clone. User should clone the
   repo fresh, run setup.bat, run_app.bat, and click through each
   dataset. Any failures feed into the next polish pass.
4. **LinkedIn post** when the app is polished. The narrative arc is
   "I built a curated reference for 12 climate datasets plus a local
   desktop tool where your API keys never leave your machine". The
   EDH streaming angle plus the privacy angle are the two hooks.
5. **Potential Python packaging upgrade**. Currently setup.bat creates
   a `.venv/`. Consider PyInstaller single-exe for non-technical users.
   User flagged as "mix of batch and conda" so a PyInstaller build
   is out of immediate scope but could be a v0.2 addition.
6. **Deferred datasets**. UKCP18 (CEDA) and GPWv4 (NASA Earthdata)
   remain stubs in `PLAN.md`. User needs to register before these can
   be built. Once credentials land, they follow the same docs + script
   + notebook + `app/dataset_pages/` pattern as the others.

## How to pick up work in a new session

1. Read this file.
2. Check `git log --oneline | head -15` to see what has landed.
3. Check `git status` for any uncommitted drift.
4. Load the `developing-with-streamlit` skill if you have not already
   (it was installed from https://github.com/streamlit/agent-skills at
   `~/.claude/skills/developing-with-streamlit/`).
5. Decide which open thread to pick up (the user will usually say).
6. Use the existing persistent memory in
   `C:\Users\alfie\.claude\projects\C--climate-data-climate-data-quickstart\memory\`
   for user and collaboration preferences.

## Key user preferences from memory

- **British English.** No em dashes, no banned words
  ("comprehensive", "robust", "leverage", etc.), sentence-case headings.
- **Plan first, then build.** Major work gets a PLAN.md-style doc or a
  short proposal before execution.
- **Primary sources only** for technical claims. Mark uncertain facts
  with `[VERIFY]`.
- **Per-dataset commits** with standardised messages.
- **Scope discipline.** Docs pages are 150-250 lines (ERA5 single levels
  is the exception at the heavy end of acceptable). No glossary, no
  recipes section. Link to ECMWF / Met Office / NCEI docs instead of
  duplicating.
- **User is on Windows.** Bash in Claude Code is MSYS-style, forward
  slashes in paths, `_netrc` not `.netrc`, LF to CRLF warnings are
  expected and harmless.
- **Claude's style in responses.** Short and direct. No filler. Lead
  with the action or the answer.

## Test credentials status as of handoff

- CDS: configured at `C:\Users\alfie\.cdsapirc`
- EDH: configured in `C:\Users\alfie\_netrc`
- NASA Earthdata: NOT configured
- CEDA: NOT configured
- EWDS (GloFAS): NOT configured

Any dataset that needs one of the not-configured patterns will grey out
its Download button and show setup instructions in the sidebar.

## Recent commits for context

```
49ca876 EDH: use ds.sizes for time-dim detection, raise explicit error on miss
26d0fd7 Fix EDH UX: short-name variables, streaming snippet, netrc platform detection
007fa86 Add Streamlit desktop app: local-only UI for all 12 datasets
8a2a057 Polish e-obs wording and labels
622b587 Verify and fix HadCET parsers, HadCRUT5 URLs, EDH longitude handling
e52c80c Rewrite ghcnd parser: single wide_to_long reshape, vectorised scaling
390f179 Fix review findings: URLs, units, config naming, code correctness
ce90cbf Add root README with dataset overview table, MIT LICENSE, update PLAN
```

## Final note

The user has been moving fast this session. They prefer building and
iterating over long upfront planning once a direction is set. Respect
that: propose, confirm briefly, ship, iterate on feedback. Do not
re-plan work that has already been decided.
