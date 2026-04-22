# Recipes tab: implementation plan

## Concept

A "Learn" mode in the Streamlit app alongside Home, Download, and Explore.
Each recipe answers a climate question using one or two datasets already in
the toolkit. The user tweaks widgets (region, time range, variable), sees
a live plot, and gets a copy-paste code block that updates to match their
selections.

Not a notebook. Not a tutorial. A guided "show me something interesting"
with portable code.

## Navigation

Add a fourth sidebar button: Home / Download / Explore / **Learn**

The Learn page shows recipe cards (similar to the Home page dataset cards).
Click a card to open that recipe.

## Recipes (v1: three or four to start)

### Recipe 1: How has UK temperature changed since 1850?

- **Datasets:** HadCRUT5 (global grid, 1850-present)
- **Widgets:** none needed, or optional region picker (UK default)
- **Plot:** Annual mean temperature anomaly time series with trend line
- **Code output:** ~15 lines: requests download, xarray open, select region,
  annual mean, matplotlib plot
- **Teaching hook:** "This is the data behind the headline global warming
  numbers. HadCRUT5 blends land stations and sea surface observations into
  a 5-degree grid."
- **Data:** open access, no credentials, tiny file, instant

### Recipe 2: ERA5 vs E-OBS - do they agree on European temperature?

- **Datasets:** ERA5 single levels + E-OBS
- **Widgets:** year (default 2023), month (default 7), variable
  (default 2m temperature)
- **Plot:** side-by-side maps (ERA5 left, E-OBS right) for same
  region/month, plus a difference map below
- **Code output:** ~30 lines: CDS API pulls for both, xarray regrid to
  common grid, difference calculation, three-panel plot
- **Teaching hook:** "Reanalysis (ERA5) and gridded observations (E-OBS)
  measure the same thing differently. Comparing them builds intuition for
  where models and observations diverge."
- **Data:** needs CDS credentials, two small pulls

### Recipe 3: What do climate models project for your region?

- **Datasets:** CMIP6 (CDS subset) or ESGF
- **Widgets:** region bbox preset (UK/Europe/custom), scenario
  (ssp245/ssp585), variable (near-surface air temperature)
- **Plot:** multi-model spread (shaded range + ensemble mean) for
  2015-2100, with historical baseline
- **Code output:** ~25 lines: CDS API pull, xarray concat, regional
  mean, spread calculation, matplotlib fill_between plot
- **Teaching hook:** "The spread across models tells you about
  uncertainty. The difference between scenarios tells you about choices."
- **Data:** needs CDS credentials, larger pull (consider pre-cached
  example data)

### Recipe 4: England's longest temperature record

- **Datasets:** HadCET (1659-present)
- **Widgets:** start year (default 1659), smoothing window (default 10yr)
- **Plot:** monthly time series with rolling mean overlay, seasonal
  cycle subplot
- **Code output:** ~15 lines: requests download, pandas read, rolling
  mean, matplotlib plot
- **Teaching hook:** "HadCET is the longest instrumental temperature
  record in the world. The seasonal cycle has stayed roughly the same
  shape for 350 years, but the baseline has shifted upward."
- **Data:** open access, no credentials, tiny file, instant

## Recipe card layout

Each recipe card on the Learn landing page shows:
- Recipe title (the question)
- One-line description
- Datasets used (with access-method badges, reuse from Home page)
- Estimated time: "instant" (open data) or "1-2 min" (CDS queue)
- Credential requirement: "none" or "CDS API key"

## Recipe page layout

When a recipe is opened:

```
[Question as heading]
[One-sentence teaching hook]

[Widgets in a row or sidebar]

[Two columns or tabs:]
  Left/Tab 1: Live plot (updates on widget change)
  Right/Tab 2: Code block (updates to match widget state)

[Copy code button]
[Link to full dataset docs]
```

## Implementation notes

### Pre-cached data

Recipes 1 and 4 (HadCRUT5, HadCET) use open-access data small enough to
download on the fly (under 1 MB each). These should work with zero setup.

Recipes 2 and 3 need CDS credentials and queue time. Options:
- Download on demand (show a spinner, could take minutes)
- Ship a tiny example file in `examples/` for instant demo, with a
  "download fresh data" button for users with credentials
- Second option is better for the "show me something" flow

### Code generation

Each recipe has a `_build_code(config)` function that returns a string.
The config dict comes from the widget state. Use `st.code(code, language="python")`
with a copy button.

The generated code must be standalone - no app imports, no common/ imports.
Just standard libraries (requests, xarray, matplotlib, cdsapi). Someone
pastes it into a fresh script and it runs.

### File structure

```
app/
  dataset_pages/
    learn.py              # Landing page with recipe cards
    recipes/
      __init__.py         # Recipe registry
      hadcrut5_trend.py   # Recipe 1
      era5_vs_eobs.py     # Recipe 2
      cmip6_projections.py # Recipe 3
      hadcet_record.py    # Recipe 4
```

### Scope control

- v1: four recipes, keep it tight
- No "build your own recipe" feature
- No conceptual explainers (what is NetCDF, what is reanalysis)
- Each recipe under 150 lines of Python
- Add more recipes later as standalone files, no framework changes needed

## What this changes about the LinkedIn post

Before: "a toolkit for downloading climate data"
After: "a toolkit for downloading, exploring, and learning from climate data"

The Learn tab gives you something to screenshot that tells a story.
A plot of 170 years of warming with "here's the code" underneath is
more compelling than a download form.

## Priority order

1. Recipe 4 (HadCET) - open data, instant, visually striking, good story
2. Recipe 1 (HadCRUT5) - open data, instant, the headline climate dataset
3. Recipe 2 (ERA5 vs E-OBS) - needs credentials but strong teaching value
4. Recipe 3 (CMIP6 projections) - needs credentials and more data, do last

## Time estimate

- Learn landing page with cards: 30 min
- Each recipe: 45-60 min
- Total for four recipes: half a day
