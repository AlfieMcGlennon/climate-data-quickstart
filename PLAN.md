# Climate data toolkit: working plan

Living document. Update as we go.

## Current phase

**Phase complete.** 12 of 14 datasets shipped. UKCP18 and GPWv4 deferred
until the user registers CEDA and NASA Earthdata accounts respectively.
Root README.md written.

## Operating decisions (from kick-off Q&A, 2026-04-19)

1. **Template build** - Autonomous end-to-end build of ERA5 Single Levels with
   self-review loops at each stage (research brief, docs, script, notebook, test,
   review). User reviews the finished template before the pipeline runs on the
   other 13.

2. **Failure handling** - Auto-retry with fixes: up to 3 test-fix cycles and 2
   review cycles per dataset. After max retries, log the failure, mark dataset
   as "needs human review" in this file, and continue to the next dataset. The
   pipeline does not block on a single failure.

3. **Commits** - One commit per dataset after it passes review. Standardised
   commit message: `Add {dataset-slug}: {short description}`. Clean history,
   easy to revert individual datasets.

4. **Earth Data Hub fallback** - If user cannot locate reference code from the
   quantum pipeline project, the researcher agent works EDH like any other
   dataset from official docs. Pipeline does not block.

## Dataset queue

Order matters. Each dataset builds on the last for narrative and technical reasons.

| # | Slug | Name | Access | Default region | Credentials | Status |
|---|------|------|--------|----------------|-------------|--------|
| 1 | era5-single-levels | ERA5 Single Levels | CDS API | UK bbox | ~/.cdsapirc | shipped (factual fixes + polish applied) |
| 2 | era5-pressure-levels | ERA5 Pressure Levels | CDS API | UK bbox | ~/.cdsapirc | shipped |
| 3 | era5-land | ERA5-Land | CDS API | UK bbox | ~/.cdsapirc | shipped |
| 4 | era5-daily-stats | ERA5 Daily Statistics | CDS API | UK bbox | ~/.cdsapirc | shipped |
| 5 | earth-data-hub | Earth Data Hub | Custom API | UK bbox | EDH token | shipped |
| 6 | hadcet | HadCET | Direct download | Central England (fixed) | None | shipped |
| 7 | hadcrut5 | HadCRUT5 | Direct download | Global (5 deg grid) | None | shipped |
| 8 | cmip6 | CMIP6 | CDS API | UK bbox | ~/.cdsapirc | shipped |
| 9 | ukcp18 | UKCP18 | CEDA | UK (full) | CEDA token (needed) | deferred: CEDA account not registered |
| 10 | glofas | GloFAS | CDS API (CEMS) | UK bbox | ~/.cdsapirc | shipped |
| 11 | ghcnd | GHCNd | Direct download | Station list (UK) | None | shipped |
| 12 | e-obs | E-OBS | CDS API | UK bbox | ~/.cdsapirc | shipped |
| 13 | gpw-population | GPWv4 | Direct download | UK bbox | ~/.netrc (Earthdata) | deferred: NASA Earthdata account not registered |
| 14 | chirps | CHIRPS | Direct download | East Africa small bbox | None | shipped |

### Order rationale

- **1 to 4 (ERA5 family)**: Build momentum. Same access pattern, same credentials,
  same output format. Establishes the template and gets four entries done quickly.
- **5 (Earth Data Hub)**: Narrative pivot. After showing the standard CDS route
  four times, introduce the streaming alternative. Strong differentiator because
  no one else documents EDH properly.
- **6, 7 (HadCET, HadCRUT5)**: Met Office direct downloads, no authentication,
  simple HTTP. Easy wins after the API-heavy start.
- **8 (CMIP6)**: Shift from reanalysis to projections. Natural conceptual transition.
- **9 (UKCP18)**: Regional high-resolution projections. Depends on CEDA account.
- **10 (GloFAS)**: Pivot to impact variables (river discharge). Still uses CDS
  (via CEMS endpoint).
- **11, 12 (GHCNd, E-OBS)**: Observational datasets. GHCNd is station-based,
  introduces that pattern. E-OBS is gridded European observations.
- **13 (GPWv4)**: Non-climate but essential for climate risk work (population
  exposure). Needs NASA Earthdata login.
- **14 (CHIRPS)**: Precipitation specialty dataset. Tropical focus, good capstone
  for showing regional/specialist datasets.

## Per-dataset configuration notes

### era5-single-levels
- Default variable: `2m_temperature`
- Test pull: 1 day, 1 variable, UK bbox
- Output: NetCDF
- Known quirks: CDS API uses long variable names (`2m_temperature`) but the
  underlying GRIB uses short names (`2t`). Document both.

### era5-pressure-levels
- Default variable: `temperature` at 850 hPa
- Test pull: 1 day, 1 variable, 1 level, UK bbox

### era5-land
- Default variable: `2m_temperature` (ERA5-Land has different variable naming than single levels)
- Higher resolution than ERA5 (0.1 deg vs 0.25 deg)

### era5-daily-stats
- Pre-computed daily aggregates. Saves the user from doing the hourly-to-daily
  conversion themselves.

### earth-data-hub
- Blocked until user provides reference code from quantum pipeline project
- Emphasise streaming vs download-and-open paradigm

### hadcet
- Central England Temperature - single time series, no spatial dimension
- Daily and monthly versions both available
- Oldest instrumental record in the world (from 1659)

### hadcrut5
- 5-degree global grid
- Anomalies, not absolute temperatures. Document the reference period clearly.

### cmip6
- Multiple models, multiple scenarios (SSPs)
- Default: one model, one scenario, for test pull

### ukcp18
- CEDA access required. User has not yet registered.
- 12km regional climate projections for UK

### glofas
- River discharge, not typical weather variables
- CEMS endpoint, not main CDS

### ghcnd
- No bbox. Use a STATIONS list instead of BBOX.
- Default: a small set of UK stations (e.g., Heathrow, Manchester)

### e-obs
- European gridded daily observations
- Reasonable UK bbox test pull

### gpw-population
- Static dataset, not time-varying
- Needs NASA Earthdata login via ~/.netrc

### chirps
- UK is outside reliable CHIRPS coverage (designed for tropical/subtropical)
- Use East Africa bbox as default (e.g., Kenya roughly: N=5, S=-5, W=34, E=42)
- Explain in docs why UK is not the default for this one

## Known blockers

1. **CEDA account** - user to register at https://services.ceda.ac.uk/cedasite/register/info/
   before dataset #9 (UKCP18)
2. **NASA Earthdata account** - user to register at https://urs.earthdata.nasa.gov/
   before dataset #13 (GPWv4)
3. **Earth Data Hub reference code** - user to locate existing code from quantum
   pipeline project before dataset #5

## Build order for scaffolding

1. Write CLAUDE.md (done)
2. Write PLAN.md (this file, done)
3. Replace Node.js .gitignore with Python-focused one
4. Create directory scaffold: `docs/`, `scripts/`, `notebooks/`, `.research/`,
   `.test_logs/`, `.review/`, `.claude/agents/`, `.claude/skills/`
5. Write `.claude/agents/researcher.md`
6. Write `.claude/agents/tester.md`
7. Write `.claude/agents/reviewer.md`
8. Do ERA5 Single Levels manually together, end to end
9. Once template quality is approved, write `.claude/skills/dataset-pipeline/SKILL.md`
10. Run remaining 13 datasets through the skill, semi-automated

## Quality gates

Before a dataset is considered "done":
- All `[VERIFY]` tags resolved or explicitly deferred to human review
- Reviewer agent score of 7 or higher
- Test log shows clean script run and clean notebook run
- Variable names identical across docs, script, and notebook
- Licence stated with attribution requirements
- Dataset added to root README.md overview table

## Out of scope for v0.1

- MCP servers
- Full CI/CD automation
- Cross-dataset comparison utilities
- Web frontend
- Docker/container distribution

Things above may come in v0.2 or later. For v0.1 the goal is: 14 datasets,
each with docs, script, notebook, runnable, reviewed.
