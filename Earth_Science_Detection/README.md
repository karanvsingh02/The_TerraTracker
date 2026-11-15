# Earth System Tracker

A local web app for investigating Earth science trends. Plain HTML, CSS, and native JavaScript modules power the interface; Python/FastAPI serves the frontend and retrieves NASA POWER data. NumPy and SciPy handle scientific calculations.

## Run locally

Requires Python 3.9 or newer and an internet connection for NASA requests.

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Open **http://127.0.0.1:8000**. Select Atmosphere, choose a variable, location and dates, then press **Retrieve & analyze**. Retrieval is explicit and may take 45 seconds. No NASA credentials are needed for POWER.

Keep the host bound to loopback. This release has no hosted authentication and must not be exposed publicly. Nothing has been deployed.

## File responsibilities

```text
frontend/
  index.html             Complete page design: header, tabs, inspector, map controls, chart and source sections
  css/styles.css           Responsive beige theme, JetBrains Mono + DM Sans, inspector and map layouts
  js/app.js                Five system routes, selection, requests and scientific result rendering
  js/catalog.js            System imagery layers and numerical variable definitions
  js/api.js                API requests and downloads
  js/chart.js              SVG time-series rendering
  js/map.js                MapLibre 2D map, NASA GIBS layers, markers, recentering and zoom
backend/
  main.py                  FastAPI routes, validation and static hosting
  catalog.py               Server-side supported variable allowlist
  adapters/power.py        NASA retrieval, normalization and bounded cache
  services/trends.py       Aggregation, regression, intervals, Mann–Kendall
 tests/test_science.py      Deterministic scientific and API tests
 docs/                     Architecture and implementation status
```

## Verify

```sh
pytest -q
```

The API's generated request/response documentation is at `/docs`. The observation endpoint is `GET /api/observations/point?lat=29.7604&lon=-95.3698&variable=T2M&start=2001-01-01&end=2024-12-31&resolution=annual`.

See [architecture](docs/architecture.md) and [implementation status](docs/status.md) for scope and scientific limitations.

## Reference redesign

The interface follows the supplied beige map reference. Its visible markup is in `frontend/index.html`; CSS and behavior remain separate for maintenance. The five tabs are Atmosphere, Geosphere, Hydrosphere, Biosphere and Cryosphere. Legacy `/land` and `/oceans` routes open Biosphere and Hydrosphere.

Run through FastAPI rather than opening the HTML with `file://`, so native JavaScript modules and `/api` requests work. MapLibre is vendored locally; NASA imagery, legends and Google Fonts require network access. GIBS layers are imagery only and do not supply numerical point readings. Atmosphere measurements come separately from POWER. The default imagery date is 2024-07-01; it is independent of the historical point-analysis period.

## Live Server previews

Keep the Python API running using the command above. Local IDE previews on ports 5500–5509 and 63342 automatically send requests to `http://127.0.0.1:8000`, with CORS limited to local origins. Alternatively open `http://127.0.0.1:8000/atmosphere` for the complete app on one server.

The side dropdown now controls the map variable for every system. All requested variables are selectable; unsupported maps show geographic context with an explicit unavailable message. Five atmosphere variables support numerical POWER retrieval; the remaining variables support imagery where configured. Run frontend regression checks with `node --test tests/frontend.test.mjs` (Node 20+).

## Trend details and map availability

Trend scores are followed by a brief summary. Select **Show more** to inspect the statistics and assumptions, or **Show less** to collapse them. Each imagery request uses a published date and discloses when it differs from the requested date. Map errors, timeouts and empty coverage are visible; **Reload map** retries the selected layer.

There are currently 24 connected imagery sources and 11 variables requiring dedicated map adapters; see [implementation status](docs/status.md) and [live map audit](docs/map-audit.json). Additional sources include SoilGrids, ITS_LIVE and regional ARIA earthquake displacement. Map availability does not imply numerical point or trend retrieval support.

To audit imagery after changing source configurations, install `requirements-map-checks.txt`, export catalog variables with a `date` from `chooseMapDate`, then run `python scripts/validate_maps.py /path/to/catalog-export.json`. This is a live network check and is separate from deterministic tests.

Selected points show a named sea/ocean/lake where available, otherwise the nearest mapped city, region, country and distance. Place labels use bundled Natural Earth data and need no external geocoding key. See backend/data/README.md for sources and geographic limitations.

Every map includes subtle Natural Earth coastline/lake-shore outlines above the data, without country borders. Fire intensity is now connected to the EUMETSAT / LSA SAF 15-minute regional FRP product (CC BY 4.0). There are now 25 connected imagery variables and ten explicitly unavailable integrations; newer status entries supersede earlier counts.

## Current map catalog

All **35** dropdown entries now have connected imagery sources. Poorly covered/unimplemented variables have been replaced explicitly after alternate-source review; groundwater and glacier mass use GFZ GravIS maps. Carbon monoxide replaces the sparse CO₂ track layer and is clearly labeled as a different gas. See [variable/source changes](docs/variable-replacements.md) for the complete mapping. Source availability, published dates and geographic masks still apply. Numerical point-analysis support remains limited to the supported NASA POWER variables.

GFZ imagery uses the Pillow dependency in requirements.txt; reinstall requirements when updating an existing environment. Its adapter preserves provider colors, crops the repeated reference world and reprojects it for MapLibre. No geocoding credentials or GFZ API keys are required.
