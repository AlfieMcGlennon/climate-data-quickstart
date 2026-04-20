# Climate data toolkit

## Project purpose

A curated, practical reference repository for climate and weather datasets.
Every output must be useful to a researcher who has never used the dataset before.
The audience is MSc/PhD students, early-career climate scientists, and climate risk analysts.

Each dataset in the repo gets three artefacts:
1. A documentation page that explains what the dataset is, what it contains, and how to access it
2. A download script with a standard config block at the top
3. A quickstart notebook that demonstrates a small, successful end-to-end pull

## Style rules

- No em dashes anywhere. Use hyphens, commas, or restructure the sentence.
- No emojis anywhere.
- No flowery language. Direct, technical, human.
- British English spelling throughout (colour, analyse, centre, licence).
- Code comments explain WHY, not WHAT.
- Variable names in docs must match the exact API variable name. No paraphrasing.
- Headings use sentence case, not title case.
- Every factual claim about a dataset must be traceable to a primary source.
- Do not use: "comprehensive", "robust", "leveraging", "utilize", "seamless", "powerful",
  "cutting-edge", "empower", "unlock", "dive into", "delve into".

## Source rules

1. PRIMARY ONLY for technical specs: official dataset documentation pages
2. SECONDARY for context: peer-reviewed papers describing the dataset
3. NEVER trust training data for variable names, API parameters, or URLs
4. If you cannot verify something against a live primary source, mark it `[VERIFY]`
5. When scanning other repos for ideas, note strengths and weaknesses in a comment block
   but never copy structure, text, or code patterns

## File naming

- Docs: `docs/{dataset-slug}/README.md`, `docs/{dataset-slug}/variables.md`
- Scripts: `scripts/{dataset_slug}_download.py`
- Notebooks: `notebooks/{dataset_slug}_quickstart.ipynb`
- Research briefs: `.research/{dataset_slug}_brief.md` (gitignored)
- Test logs: `.test_logs/{dataset_slug}.log` (gitignored)
- Review reports: `.review/{dataset_slug}_review.md` (gitignored)

Slugs use hyphens in directory names (dataset-slug) and underscores in Python filenames
(dataset_slug). This matches Python import conventions.

## Access patterns

Datasets in this repo fall into one of three access patterns. Each pattern has its own
credential file, Python client, and error handling conventions.

### Pattern A: Copernicus CDS API
- Used for: ERA5 (all variants), ERA5 Daily Statistics, CMIP6, E-OBS, GloFAS
- Python package: `cdsapi`
- Credentials: `~/.cdsapirc` (url + key)
- Client: `cdsapi.Client()` (reads credentials automatically)
- Queue behaviour: requests are queued server-side, can take minutes to hours
- Output format: NetCDF or GRIB

### Pattern B: Direct download
- Used for: HadCET, HadCRUT5, GHCNd, CHIRPS, GPWv4
- Python package: `requests` or `urllib`, sometimes `wget` for bulk
- Credentials: varies. HadCET and HadCRUT5 are open. GPWv4 needs NASA Earthdata login
  via `~/.netrc`. CHIRPS is open via HTTPS.
- Output format: varies (text, CSV, NetCDF, GeoTIFF)

### Pattern C: Custom Python API
- Used for: Earth Data Hub (streaming), UKCP18 via CEDA
- Python package: dataset-specific (Earth Data Hub has its own client; CEDA uses
  bearer tokens over HTTPS)
- Credentials: dataset-specific token files or environment variables
- Output format: typically xarray datasets directly, no intermediate file

## Config block standard

Every download script and notebook begins with this block, adapted per dataset:

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

Rules:
- Config block is always the first executable code in the file
- Values must be sensible defaults that produce a small, fast test pull
- BBOX defaults to UK for datasets where UK is within coverage
- For datasets where UK is not in coverage (e.g., CHIRPS is quasi-global but
  primarily tropical), use a dataset-appropriate small region and state why in a comment
- Station-based datasets (GHCNd) replace BBOX with a STATIONS list
- OUTPUT_DIR is always a relative path, never absolute

## API key handling

- Keys live in standard config files (`~/.cdsapirc`, `~/.netrc`, etc.)
- Scripts reference keys via standard library mechanisms (`cdsapi.Client()` reads
  `~/.cdsapirc` automatically)
- NEVER print, log, or commit keys
- Scripts must check for key existence and fail with a clear message if missing.
  Example:
  ```python
  if not Path("~/.cdsapirc").expanduser().exists():
      raise FileNotFoundError(
          "CDS credentials not found at ~/.cdsapirc. "
          "Register at https://cds.climate.copernicus.eu and follow "
          "https://cds.climate.copernicus.eu/how-to-api"
      )
  ```
- `.gitignore` excludes: `.cdsapirc`, `.netrc`, `*.key`, `*.token`, `data/`,
  `.research/`, `.test_logs/`, `.review/`

## Notebook standards

Every notebook must be runnable top-to-bottom without modification after the user
has edited the config block. Fixed six-cell structure:

1. **Config block** (code cell)
2. **Imports with version check** (code cell) - imports + `print(xr.__version__)` style
3. **Download** (code cell) - small test pull, 1 day, 1 variable, small region
4. **Open with xarray** (code cell) - `ds = xr.open_dataset(...)`, print dataset summary
5. **Basic plot** (code cell) - map or time series, whichever fits the dataset
6. **Next steps** (markdown cell) - pointer to full docs, suggested extensions

Plots must have labelled axes, units, and a colourbar label if they are maps.

## Python standards

- Type hints on all function signatures
- Docstrings on all functions (Google style)
- No wildcard imports
- Core requirements: `cdsapi`, `xarray`, `netcdf4`, `matplotlib`, `cartopy`, `numpy`, `pandas`
- Per-dataset extras go in the dataset's docs, not the top-level requirements
- Target Python 3.10+

## Agent workflow

This project uses a three-stage pipeline per dataset:

1. **Research subagent** gathers specs from primary sources, writes brief to
   `.research/{dataset_slug}_brief.md`
2. **Main session** writes docs, script, and notebook using the brief
3. **Test subagent** validates code by running a minimal download, logs results
4. **Review subagent** checks quality, consistency, and adherence to these rules

Agent definitions live in `.claude/agents/`. The orchestration skill lives in
`.claude/skills/dataset-pipeline/`.

IMPORTANT: When processing a dataset, always start by reading the research brief
from `.research/{dataset_slug}_brief.md`. Do not skip this step. If the brief does
not exist, invoke the researcher agent first.

## Working state

Current status, dataset queue, and per-dataset configuration live in `PLAN.md`.
Always read `PLAN.md` before starting work on a new dataset.
