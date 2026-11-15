# Implementation and validation status

## Implemented

- Responsive dashboard, sidebar, all requested routes, return navigation, reduced-motion support.
- Atmosphere variable selection, coordinate entry, clickable/keyboard geographic point selector, date and aggregation controls.
- Server-side NASA POWER adapter for six variables; native units, null fill values, source attribution and timestamps.
- SVG observations and fitted trend, raw CSV export with provenance, SVG chart export.
- Annual/monthly aggregation, optional monthly deseasonalization, regression, slope intervals, tie-corrected Mann–Kendall, completeness and autocorrelation disclosures.
- Loading, validation, unavailable-source and analysis-unavailable states.

## Explicitly pending

Additional geographic boundary overlays; geographic search; polygon/bounding-box selection and area weighting; region comparison; Three.js globe (the current reference design intentionally uses only 2D maps); dedicated latest-data mode; Theil–Sen and seasonal/autocorrelation-adjusted tests; AppEEARS, Oceans, GISTEMP and Cryosphere adapters; persistent jobs/storage; hosted authentication; public or private deployment.

The supplied beige reference is now the design basis. The visible page structure lives directly in frontend/tracker.html. Five top tabs replace sidebar navigation. A scrollable point inspector accompanies the MapLibre map. Each system has its own NASA GIBS imagery layer and provider legend where supplied. Clicking a point recenters the map; Atmosphere automatically retrieves POWER observations. Other systems support imagery viewing only, with numerical measurements explicitly unavailable. The illustrated AOD/PM/ozone readings in the reference have not been copied as observations.

## Validation

Deterministic pytest cases cover known slopes, constant data, missing values, partial periods, precipitation totals, circular-variable guard, test statistics, route availability, invalid input, and a mocked end-to-end API pipeline. Mocked tests do not validate the external NASA service. Browser interaction and live-provider verification must be recorded separately; see final delivery notes for checks performed in this session.

Live verification: a genuine NASA POWER request for Houston (29.7604, -95.3698), T2M, 2024-01-01 through 2024-01-07 returned seven daily rows, native unit C, and latest selected observation 2024-01-07. This validates one point-variable-period only, not every parameter or multi-decade availability.

Local verification: all nine pytest cases passed; JavaScript syntax checks passed for the application, chart, and map modules. Interactive browser and mobile visual testing were not performed.

Redesign checks: all nine existing pytest tests passed; JavaScript syntax checks passed; all five system pages and CSS/JS/vendor assets returned HTTP 200 through FastAPI TestClient. NASA GetCapabilities confirmed the configured layers and legends; a real aerosol GetMap request returned a PNG. Interactive browser rendering has not been visually verified in this environment.

## Variable-driven maps and local preview fix

All 35 requested variables are listed across the five system dropdowns; blank table rows are omitted. The separate map selector is removed. Selecting a variable selects its explicit GIBS layer, legend, and provider. Variables without connected layers remove the prior overlay and label the basemap as geographic context only. Numerical retrieval is supported for atmospheric temperature, surface pressure, precipitation, total column water vapor and solar radiation. Other entries disclose unavailable numerical extraction.

Monthly and annual map requests use period-aligned dates; static composites are labeled. Ozone imagery shows total-column ozone, methane imagery shows 400 hPa mixing ratios, currents show the zonal component, and sea level shows height anomalies; these qualifications appear in the inspector.

Localhost previews target the Python API on 127.0.0.1:8000. The backend permits CORS only for local IDE origins on ports 5500–5509 and 63342. It must remain running for numerical retrieval. Tab navigation uses query parameters, allowing Live Server refreshes to retain the actual HTML file path.

Verification: 11 Python tests and four Node regression tests passed. Live NASA POWER responses confirmed TQV and solar radiation, including current native units kg m-2 and MJ/m^2/day. Numerical values always use returned units, rather than assuming a display conversion.

## Trend summary and map audit

Trend analysis retains the two headline scores. A deterministic, one-to-two sentence summary describes the direction, approximate change and strength of evidence. Technical intervals, both test results, fit, residual correlation, completeness and caveats are collapsed behind a keyboard-accessible Show more / Show less button. The detail layout uses labeled rows and separate interpretation/limitations sections.

Map requests now select actual available dates, including monthly and annual spacing, multi-day products, catalog gaps, ended products and one-date composites. The displayed date explicitly identifies any substitution. The app refreshes provider availability metadata at runtime, retaining saved dates if that request fails.

Map loading has a deadline, persistent error states, a Reload map action and a browser image-alpha check for an empty viewport. Viewport checks use the map's EPSG:3857 projection. Tile errors are not cleared by a later idle event. Coverage gaps are distinguished from zero measurements.

Added sources: SoilGrids modeled clay content at 0–5 cm, ITS_LIVE glacier velocity reference tiles, and ARIA line-of-sight displacement for the February 2023 Türkiye earthquakes. Regional/composite limits are explicit. These are map integrations; numerical time-series extraction has not been added for them.

A live audit decoded nontransparent images from all 24 configured sources. See map-audit.json. This checks service access and image content for the recorded date and view, not scientific validity at every location or numerical observation extraction. Optional audit dependency: requirements-map-checks.txt.

Eleven requested variables still lack connected map adapters: gravity anomaly, surface roughness, land subsidence, tectonic movement, ice thickness, ice sheet elevation, ice mass, vegetation cover, fire intensity, wave height and groundwater storage. These are not represented by substitute imagery. Research found source products, but did not establish a working and scientifically suitable map integration for each. The app continues to identify them as unavailable. The investigated Australian gravity service returned HTTP 403; the accessible Bedmap catalog exposed survey-point layers rather than the requested gridded thickness/elevation products.

Browser verification in installed Chrome: a real NASA POWER request succeeded, the summary appeared, Show more/Show less expanded and collapsed details, the ended solar layer displayed its actual 2021 date, unavailable variables were labeled, and the mobile viewport had no horizontal overflow. No JavaScript runtime errors were recorded. Connected temperature, soil, glacier-velocity and historical sea-level maps completed loading. Automated regression checks include empty transparent images, persistent tile errors, temporal coverage and summary/toggle behavior.

Legend layout update: SoilGrids clay-content keys now render as a horizontal HTML color bar, using the 33 provider colors and labels from its published legend, with upright value labels and g/kg units. Other provider keys retain their horizontal graphics without the previous height cap; wide keys scroll sideways. Chrome verification confirmed a 296×16 px soil ramp, readable ticks, no mobile horizontal page overflow and no runtime errors.

Place-name update: selected coordinates now resolve through `/api/places/reverse` to named marine regions or lakes, with a nearest-indexed-city label and great-circle distance elsewhere. Public-domain Natural Earth reference data are bundled in backend/data, so runtime place lookup makes no third-party requests. Names and marine boundaries are approximate; the nearest city is from the reference gazetteer, not every possible settlement. The user's example 26.76 N, 17.56 W resolves to Atlantic Ocean. Lookups are cached, independently canceled and protected against stale responses after another point is selected.

## Shoreline overlay and fire-source connection

Natural Earth 1:10m coastlines and named-lake shorelines are bundled locally, with line geometry only. Faint near-black strokes render above every scientific raster and remain visible when changing tabs or variables. No country borders are included. Native geometry is preserved, and large GeoJSON responses are gzip-compressed by the app server. See frontend/data/README.md for source/scale limitations.

Fire intensity now uses actual Fire Radiative Power from EUMETSAT / LSA SAF's MSG-FRP public WMS, with provider style, 15-minute timestamps, a horizontal MW legend and regional coverage disclosure. Availability metadata refreshes from that provider, and time selection preserves hours/minutes instead of truncating timestamps to dates. A real PNG and browser-rendered layer were verified. Attribution: EUMETSAT / LSA SAF, CC BY 4.0; https://lsa-saf.eumetsat.int/en/data/map-service/.

Current total: 25 connected imagery variables; ten unimplemented map adapters remain (gravity anomaly, surface roughness, land subsidence, tectonic movement, ice thickness, ice sheet elevation, ice mass, vegetation cover, wave height, groundwater storage). Unavailable entries are clearly marked in the dropdown and map rather than described as an internet connection failure.

Validation: 13 Node regression tests and 14 Python tests passed. Chrome verified both shoreline files loading with gzip, the new fire layer completing loading with its actual timestamp, and no JavaScript runtime errors. The shoreline regression check confirms science rasters are inserted below coastlines and lake outlines survive variable switches.

## Current coverage-based catalog (supersedes earlier pending lists)

All 35 dropdown entries now have connected imagery sources. Two formerly unsupported concepts are retained using GFZ GravIS groundwater/glacier-mass anomalies; nine entries are explicitly replaced with relevant NASA variables. See variable-replacements.md and variable-replacements.json for the exact changes, alternate-source review and scientific distinctions. All 35 sources returned nontransparent images for the recorded audit requests. Chrome verified the new CO and GFZ layers. Fourteen Node tests and seventeen Python tests passed. Existing numerical trend support remains scoped to NASA POWER.

## Numerical extraction and coverage update — November 14, 2026

The imagery catalog and numerical pipelines are separate. The point API now supports persistent asynchronous extractions and browser polling, with source-specific metadata and cancellation. NASA AppEEARS profiles are connected for surface/root-zone moisture, soil temperature, snow water equivalent, evapotranspiration, land temperature, NDVI, productivity, snow cover, freeze/thaw and annual land-cover classes. Land-cover analysis reports observed category changes rather than regressing class codes. These profiles need individual live validation; a real NDVI extraction was verified (three monthly observations, scaled values and QA). A SMAP timestamp-validation extraction remains queued at NASA.

NASA JPL MUR data served through NOAA ERDDAP now supply sea temperature, sea-temperature anomaly and sea-ice fraction. SST was verified with real observations at 44.02 N, 87.25 W, including the selected July 1, 2024 value of 17.061°C and three monthly means. Chrome verified the selected-date readout, history chart, trend results, and absence of JavaScript errors. Monthly SST extraction uses the provider's monthly `sst` variable, not the daily `analysed_sst` field. Missing ocean pixels stay missing. Complete requested calendar months are required for monthly composites.

Ozone imagery now uses MERRA-2 monthly ozone mixing ratio at 50 hPa instead of patchy OMI total-column swaths. This is an explicitly renamed physical quantity, with a matching legend. The map response was verified. Numerical ozone is still unconnected: the legacy GES DISC endpoint returned 410 and its current cloud endpoint returned 403 with the configured account. No EULA or application authorization was accepted programmatically.

Snow-water-equivalent imagery now uses ongoing SMAP L4 snow mass, with published imagery through November 2026, replacing AMSR2's September 2025 cutoff. Ocean/permanent-ice and retrieval-quality masks remain intentional. This does not resolve all remaining imagery-only products: CO, methane, elevation, displacement, soil composition, albedo, glacier mass/velocity, ice temperature, biomass, salinity, sea level, currents and groundwater still need appropriate numerical integrations. Static maps cannot supply a valid historical trend on their own. The regional displacement map also remains an event composite.

Validation at this update: 22 Python tests and 14 Node tests passed; live SST and NDVI extractions and the ozone replacement image were checked. AppEEARS profile registration does not mean all eleven products have completed live extraction validation.

## Ozone numerical source and window tabs — November 15, 2026

OZONE now means **total-column ozone (DU)** from KNMI/TEMIS MSR2, replacing the imagery-only MERRA-2 50 hPa mixing-ratio product. Its public 0.5° monthly NetCDF archive provides both the rendered map and native point histories, through December 2025. No Earthdata authorization is required. The adapter parses the classic 64-bit-offset NetCDF header and makes bounded HTTP range requests for specific point samples or a monthly grid. It rejects HTTP 200/full-file responses to prevent accidentally downloading the ~800 MB archive. Fill values remain missing; no colors are interpreted as measurements. Numerical analysis excludes incomplete requested calendar months. Public metadata updates map availability; archive values and dates were validated live. Houston January–March 2024 point values were 286, 281, and 298 DU; the browser loaded a full year, displayed 284 DU as its latest observation, and showed the chart and trend analysis.

MSR2 attribution and documentation: https://temis.pmc.knmi.cloud/protocols/O3global.php ; dataset DOI https://doi.org/10.21944/temis-ozone-msr2 . This is historical reanalysis, not a near-real-time surface-air-quality product. NASA POWER TO3 was also verified as an alternative total-column series, but was not mixed into the KNMI map/history.

The completed NASA SWE test exposed timestamps formatted `2024-01-01 01:30:00 UTC`. The parser now handles this format and retains all sixteen distinct three-hourly observations over the two-day test, rather than discarding them. The selected test point is in Lake Michigan, outside SMAP's land measurement domain; successful extraction does not establish valid snow measurements over water.

The sphere navigation spans exactly the combined inspector/map width, with window-style rectangular tabs and one shared brown highlight. Transform-based animation moves left or right; ResizeObserver and font-ready layout maintain alignment after resizing. Reduced-motion preferences disable animation, and all five tabs fit at 390 px without horizontal page overflow. Chrome verified initial alignment, both movement directions, mobile switching, the ozone side-panel/chart pipeline, and no JavaScript runtime errors. The pending provider-image load handler is cleared on legend switches so a stale graphic cannot appear above a custom scale.

Current automated verification: 25 Python tests and 14 Node tests pass. Other remaining imagery-only variables listed above are not claimed to have numerical support by this update.

## Point-selection stability and today's date — November 15, 2026

Point, sphere, selected variable and explicit imagery dates are retained in URL query parameters. Reloading the document restores the marker and variable instead of reverting to air temperature; clearing a point removes its saved coordinates. Automatic imagery dates use the browser's local calendar day, recalculated on each load, rather than the hardcoded July 2024 date. Explicit user-selected dates remain preserved. Dataset availability still determines the actual displayed observation, with the fallback date labeled (for example, today's ozone request displays the December 2025 monthly record).

Map updates now compare source/date signatures before rebuilding a layer; unchanged metadata refreshes leave it in place. Reload map explicitly bypasses this guard. A selected point prevents a product's default camera preset from overriding the user's location. Rapid selections stop the previous camera animation. Live Server workspace exclusions cover `.runtime`, Python runtime files, and local credentials so generated extraction database writes do not trigger document refreshes.

Chrome regression verification used actual map clicks, rapid repeated selections, document reloads, a custom imagery date and clear-point actions. Ozone remained selected, one marker remained at the last selected coordinates, map clicks caused no document navigation, and the default requested date was November 15, 2026. No JavaScript errors occurred. Numerical API responses were fixture-controlled for this interaction regression. Existing live numerical validation remains documented above. Fifteen Node and twenty-five Python tests passed.

## Exact investigation-date windows — November 15, 2026

Every numerical provider now passes through the shared `select_period`/`finish` contract, including the formerly separate POWER path. Results retain `requestedStart`/`requestedEnd` and separately identify returned observation bounds. Samples outside the chosen window are removed before analysis. Monthly, annual, 8-day and 16-day composites must fit entirely inside the requested dates. Aggregation also excludes calendar buckets extending outside the selected period, even if a partial year would otherwise meet the 90% completeness threshold. SMAP's centered three-hour intervals and SMOS's centered 72-hour composites retain their true time support. Older cached results are migrated through the same range contract without resubmitting NASA extraction tasks.

The SVG timeline uses the exact input dates as its domain and end labels, leaving blank space where observations are unavailable. It defensively filters plotted/fitted points outside those bounds. Static reference values are explicitly shown without a fabricated historical timeline. The source-observation period is separate from the requested period. Changing map imagery date no longer restarts the unchanged graph query; map date and graph From/To controls are labeled as separate functions.

Date/resolution edits refresh the selected point's results after a short debounce. From/To settings are remembered per sphere/variable and in the URL. Dataset metadata callbacks do not overwrite edited dates. Source record limits no longer silently replace the user's selected range; unavailable periods instead receive a coverage message. Ocean map-date preview readings are only requested when the map date lies inside the chosen analysis period.

Verification: Chrome checked submitted and automatically updated periods in all five spheres, exact SVG labels, tab switching, and reload persistence, with no JavaScript errors (provider responses controlled for the UI regression). Live API checks returned all 42 requested daily T2M values for January 10–February 20, 2024, and seven complete LST composites within January 10–March 15, 2024 (first January 17, last March 5). The graph retains January 10 and March 15 as its axis bounds, rather than relabeling the range to those observation dates. Forty Python and seventeen Node tests passed, including all five spheres and six native temporal cadences.
