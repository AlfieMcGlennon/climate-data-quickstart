# Climate data learn: plan and handoff

A standalone Streamlit app that makes real climate data accessible to
learners from KS2 to postgraduate level. Built on the same Python
patterns as climate-data-quickstart but with pedagogical framing,
guided questions, and age-differentiated depth.

## Relationship to existing projects

### climate-data-quickstart (this repo)
- **Role:** upstream pattern library and data pipeline reference
- **What transfers:** recipe architecture, `@st.cache_data` pattern,
  `_build_*_code()` snippet generators, widget-driven plots, open-access
  dataset download functions
- **What does not transfer:** practitioner-facing prose, download forms,
  credential management, the 17-dataset breadth

### climate-playbook (Next.js)
- **Role:** pedagogical framework and content platform
- **What it keeps:** Pillars 1, 3, 4, 5 (science spine, governance,
  curriculum mapping, climate week) stay as MDX pages. The JavaScript
  simulators (Simple Climate Model, Carbon Budget Calculator) stay as
  in-page widgets for quick conceptual demos.
- **What changes:** Pillar 2 (Data Pathway) links out to the new
  Streamlit app for hands-on data work. The existing Data Explorer
  simulator becomes a teaser/intro, not the main tool.
- **Linkage:** Pillar 2 pages provide framing ("what is a temperature
  anomaly?") then link to the Streamlit app ("now explore the real
  data"). A-level Computing in Pillar 4 links to recipes as worked
  Python examples.

### climate-data-learn (new repo)
- **Role:** the interactive data teaching app
- **Hosting:** Streamlit Community Cloud (free, Python runs server-side,
  students visit a URL, no install)
- **Audience:** KS2 through postgrad, plus curious public
- **Content:** guided recipes with real open-access climate data

## Architecture

```
climate-data-learn/
  app/
    main.py                    # Entry point, sidebar, level selector
    levels.py                  # KS2, KS3, GCSE, A-level, Advanced
    recipes/
      __init__.py              # Recipe registry
      hadcet_record.py         # England's temperature since 1659
      hadcrut5_trend.py        # Global warming since 1850
      chirps_rainfall.py       # Tropical rainfall patterns
      arco_era5_weather.py     # What does weather look like as data?
      esgf_projections.py      # What do climate models predict?
      ecmwf_forecast.py        # How does a weather forecast work?
    common/
      data_loader.py           # Cached download functions (from quickstart)
      code_builder.py          # Snippet generators (from quickstart)
      plot_helpers.py          # Shared plot defaults
  .streamlit/
    config.toml                # Theme (match playbook palette if desired)
  requirements.txt
  README.md
```

### Key design decisions

**No credentials required.** Only use datasets with open access:
- HadCET (Met Office, direct HTTP, no auth)
- HadCRUT5 (Met Office, direct HTTP, no auth)
- CHIRPS (UCSB, direct HTTP, no auth)
- ARCO-ERA5 (Google Cloud Storage, public Zarr, no auth)
- ESGF CMIP6 (direct HTTP, no auth)
- ECMWF Open Data (direct HTTP, no auth)

**Python runs server-side.** Students never install Python. Streamlit
Community Cloud runs the app on their infrastructure. Students visit
a URL in any browser. This works on school Chromebooks, iPads, phones.

**Code is shown, not executed by students.** Students see the Python
that produced each plot. They can copy it if they want to run it
themselves (A-level and above). But the app does not embed a code
editor or REPL. The teaching value is in reading and understanding
code, not in debugging syntax errors.

**Age differentiation via tabs, not separate pages.** Each recipe has
a level selector (KS2 / KS3 / GCSE / A-level / Advanced). The data
and plots are identical. What changes:
- Prose complexity and vocabulary
- Which questions are asked
- Whether code is shown
- Depth of explanation

## Level framework

### KS2 (ages 7-11)
- **Prose:** simple sentences, no jargon, analogy-heavy
- **Code:** hidden entirely
- **Interaction:** big sliders, colour-coded plots, guided observations
- **Questions:** "What do you notice?", "When does it change?",
  "What might happen next?"
- **Example:** "This chart shows how warm England has been for over 350
  years. Each tiny dot is one month. The red line smooths it all out so
  you can see the big picture. What happens to the red line after 1900?"

### KS3 (ages 11-14)
- **Prose:** introduces technical terms with definitions inline
- **Code:** hidden by default, expandable for curious students
- **Interaction:** sliders with labelled effects ("smoothing window",
  "baseline period")
- **Questions:** "What happens when you change X?", "Why does the
  choice of baseline matter?", "How is this different from weather?"
- **Example:** "A rolling mean averages the temperature over a window
  of time. Try changing the window from 10 years to 50 years. What
  happens to the line? Why might a scientist choose a longer window?"

### GCSE (ages 14-16)
- **Prose:** technical, matches GCSE geography/science vocabulary
- **Code:** shown in simplified form, annotated line-by-line
- **Interaction:** full widget set, with explanations of what each
  parameter controls
- **Questions:** "Compare baselines 1961-1990 and 1850-1900. Which
  makes recent warming appear larger? The IPCC uses 1850-1900 - why
  might that be a better choice for measuring total human influence?"
- **Example:** "The code below downloads real temperature data from the
  Met Office. Line 3 calculates the average temperature during your
  chosen baseline period. Line 4 subtracts that average from every
  data point, converting absolute temperatures into anomalies."

### A-level (ages 16-18)
- **Prose:** assumes climate science fundamentals, focuses on method
- **Code:** full standalone Python, copyable, with brief comments
- **Interaction:** all widgets, plus raw data preview (dataframe view)
- **Questions:** "Modify the code to compare HadCET with HadCRUT5.
  Does England warm faster than the global average? What physical
  mechanisms explain this?", "Why does the ensemble spread widen with
  lead time in the seasonal forecast?"
- **Example:** the recipe code as-is from climate-data-quickstart

### Advanced (undergrad/postgrad/professional)
- **Prose:** minimal, assumes domain knowledge
- **Code:** full standalone Python with extension suggestions
- **Interaction:** all widgets, raw data, download buttons
- **Questions:** open-ended research prompts
- **Example:** the recipe code plus "try this next" extensions

## Recipes to build (priority order)

### 1. England's longest temperature record (HadCET)
- **Data:** monthly mean temp, 1659-present, ~50 KB
- **Plots:** trend with rolling mean, seasonal cycle comparison,
  decade bars
- **Teaching hooks:** longest instrumental record, what is a rolling
  mean, why does smoothing help, seasonal vs long-term change
- **All levels work** because the data is simple (date + temperature)
  and the story is intuitive

### 2. How much has the world warmed? (HadCRUT5)
- **Data:** global monthly anomaly summary, 1850-present, ~200 KB
- **Plots:** bar chart with rolling mean, warming stripes, decadal
  averages
- **Teaching hooks:** what is an anomaly, what is a baseline, why
  do scientists use anomalies instead of absolute temperature, the
  acceleration of warming
- **Warming stripes are the hero visual** - instantly recognisable,
  extremely shareable, connects to Ed Hawkins' work

### 3. What does weather look like as data? (ARCO-ERA5)
- **Data:** single time step of global temperature/pressure/wind from
  ERA5 via Google Cloud Zarr, streamed on demand
- **Plots:** global map of temperature, wind vectors, pressure field
- **Teaching hooks:** reanalysis vs observation, what a grid is, how
  weather maps are made from data, latitude/longitude, map projections
- **KS2/KS3 entry point:** "this is what the weather looked like on
  [date] - here is the temperature everywhere on Earth at the same
  time"

### 4. Where does it rain? (CHIRPS)
- **Data:** monthly rainfall, tropical band, ~5 MB for one month
- **Plots:** rainfall map, zonal mean, seasonal cycle for a region
- **Teaching hooks:** satellite vs station data, why rainfall matters
  for food security, monsoon patterns, drought detection
- **Cross-curricular:** geography (monsoons, tropical climates),
  biology (crop yields), maths (spatial averaging)

### 5. What do climate models predict? (ESGF CMIP6)
- **Data:** one model, one scenario, global temperature, ~10 MB
- **Plots:** historical + projection time series, multi-model spread
- **Teaching hooks:** what is a scenario (SSP), why do models disagree,
  uncertainty vs ignorance, what we can and cannot predict
- **A-level and above:** ensemble spread, model weighting, the "hot
  model" problem

### 6. How does a weather forecast work? (ECMWF Open Data)
- **Data:** latest IFS forecast, 0-10 days ahead, ~20 MB
- **Plots:** forecast map at different lead times, skill decay chart
- **Teaching hooks:** deterministic vs probabilistic, why forecasts
  get worse with time, how forecast models differ from climate models
- **Engaging for younger students:** "what will the weather be on
  Saturday?" with real NWP data

## Implementation plan

### Phase 1: port and reframe (1-2 days)
1. Create the new repo with the directory structure above
2. Copy the recipe pattern from climate-data-quickstart (data loading,
   caching, code generation, plot rendering)
3. Build the level selector component (tabs or segmented control)
4. Rewrite HadCET and HadCRUT5 recipes with all five level variants
5. Deploy to Streamlit Community Cloud, confirm it works on a phone

### Phase 2: new recipes (2-3 days)
6. Build ARCO-ERA5 recipe ("what does weather look like as data?")
7. Build CHIRPS recipe ("where does it rain?")
8. Build ESGF recipe ("what do climate models predict?")
9. Build ECMWF Open Data recipe ("how does a forecast work?")

### Phase 3: playbook integration (1 day)
10. Update Pillar 2 (Data Pathway) pages to link to the Streamlit app
11. Add A-level Computing links in Pillar 4
12. Update playbook README and ROADMAP to reflect the new architecture

### Phase 4: polish (1 day)
13. Theme alignment (match playbook palette or establish sibling brand)
14. Add a "for teachers" page explaining how to use in class
15. Add print/export for plots (students can paste into assignments)
16. Mobile testing (school Chromebooks, iPads)

## Known issues and gotchas

### Streamlit Community Cloud limits
- **Memory:** 1 GB per app. ARCO-ERA5 and ESGF data must be carefully
  subsetted. Never load a full global field at full resolution.
- **Spindown:** free apps sleep after inactivity. First load after
  sleep takes 30-60 seconds. Warn students/teachers about this.
- **Concurrent users:** limited. If a whole class hits it at once,
  it may slow down. For classroom use, consider running locally on
  the teacher's machine and projecting, or having students work in
  small groups.
- **No persistent storage.** Downloaded data is cached in memory
  only. Each session re-downloads. The datasets are small enough
  (KB to low MB) that this is fine.

### Data reliability
- **HadCET and HadCRUT5** are extremely stable. Met Office URLs have
  not changed in years. Low risk.
- **ARCO-ERA5** is a public Google Cloud bucket. Google could change
  access or throttle. Medium risk. Have a fallback message.
- **ESGF nodes** go down periodically. The download function should
  try multiple nodes and show a clear error if all fail.
- **ECMWF Open Data** is reliable but the latest forecast rotates
  every 6 hours. The recipe should handle "forecast not yet available"
  gracefully.
- **CHIRPS** is hosted by UCSB. Stable but occasionally slow. Set
  generous timeouts.

### Cartopy on Streamlit Cloud
- Cartopy requires system-level libraries (GEOS, PROJ). On Streamlit
  Community Cloud, add a `packages.txt` file containing:
  ```
  libgeos-dev
  libproj-dev
  proj-data
  proj-bin
  ```
  This installs the C dependencies before pip runs.

### Code snippet accuracy
- Every code snippet must be fully standalone and runnable. A student
  who copies a snippet into a fresh Python file or Colab notebook must
  get a working result. No "assumes variable X from above" shortcuts.
- Test every snippet manually before shipping.

### Age-appropriate language
- KS2 prose must be reviewed by someone who works with that age group.
  Scientists (and AI) consistently overestimate what 8-year-olds
  understand. Get a primary teacher to read it.
- Avoid: "anomaly" at KS2 (say "how much warmer or cooler than
  normal"), "baseline" at KS2/KS3 (say "the average we compare to"),
  "reanalysis" below A-level (say "a weather map made by a computer
  using millions of measurements").

### Accessibility
- All plots need alt text (Streamlit supports this via st.pyplot's
  caption or a st.caption below).
- Colour palettes must work for colour-blind students. RdBu_r
  (red-blue diverging) is acceptable. Avoid red-green.
- Font sizes in plots should be legible on a projected screen (14pt
  minimum for axis labels).

## Framing for the Royal Met Soc / Reading University

**Pitch:** "We took real Met Office and ECMWF data and made it
accessible from age 8 to postgraduate, using the same tool. A KS2
student sees a chart and answers 'what do you notice?' An A-level
student sees the Python that made the chart and modifies it. A
postgrad copies the code into their own research workflow. Same data,
same questions, different depth."

**What makes it different from existing resources:**
- Uses real, current data (not static images or toy datasets)
- Progressive disclosure from visual-only to full Python
- Runs in a browser, no install, works on school Chromebooks
- Aligned to UK curriculum (KS2-A-level, mapped to subject specs)
- Open source, free, no login required

**What it is NOT:**
- Not a replacement for teaching. It is a tool teachers use in lessons.
- Not a coding course. The code is shown for transparency and for
  students who want to go further, but the primary interaction is
  through widgets and guided questions.
- Not comprehensive. Six datasets, six recipes. Depth over breadth.

## Linkage pattern between playbook and data app

### In the playbook (Next.js)

Pillar 2 lesson pages include a callout component:

```mdx
<DataAppLink
  recipe="hadcrut5_trend"
  level="gcse"
  title="Explore real global temperature data"
  description="Open the interactive data app to see 175 years of
  warming from the Met Office's HadCRUT5 dataset."
/>
```

This renders as a styled card with a button that opens the Streamlit
app in a new tab, deep-linked to the right recipe and level:

```
https://climate-data-learn.streamlit.app/?recipe=hadcrut5_trend&level=gcse
```

### In the data app (Streamlit)

The app reads `recipe` and `level` from query params on load:

```python
recipe_id = st.query_params.get("recipe", None)
level = st.query_params.get("level", "gcse")

if recipe_id:
    # Jump straight to the recipe at the right level
    render_recipe(recipe_id, level)
else:
    # Show the recipe gallery
    render_gallery()
```

A "back to lesson" link at the top returns to the playbook page that
sent them.

### Deep linking both ways

Each recipe page in the data app has a footer:

```
Learn more about [temperature anomalies / climate models / etc.]
in the Climate Playbook: [link to relevant Pillar 2 lesson]
```

Each Pillar 2 lesson in the playbook has the DataAppLink callout
above. Students can move between conceptual learning and hands-on
data exploration without losing context.

## Theme and branding

Two options:

**Option A: sibling branding.** Same colour palette as the playbook
(warm teal/earth tones), same fonts (Source Serif 4 + Inter), "Climate
Playbook: Data Lab" as the title. Feels like part of the same product.

**Option B: independent branding.** The data app has its own identity
(closer to climate-data-quickstart's current look). Linked from the
playbook but not branded as part of it. More flexible if you want to
share it independently.

Recommendation: **Option A for the POC showcase.** It strengthens the
pitch to show an integrated product. You can always rebrand later.

## What to do now

1. **Thursday:** post climate-data-quickstart to LinkedIn. Mention that
   a teaching-focused version is in progress.
2. **This week:** create the climate-data-learn repo. Port HadCET and
   HadCRUT5 recipes with level variants. Deploy to Streamlit Cloud.
3. **Next week:** build remaining recipes. Update playbook Pillar 2.
4. **When ready:** second LinkedIn post. Share with Royal Met Soc and
   Reading contacts.
