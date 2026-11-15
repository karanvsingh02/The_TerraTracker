# Coverage-based source review

The user authorized replacing poorly covered variables only after checking alternate sources. This review changes variable names and explanations explicitly; it never shows a different physical measurement under an old label. All 35 offered variables now have a configured imagery source and returned a nontransparent image in the recorded live checks. This is a visualization-access check, not a guarantee of observations at every point, date or pixel.

## Preserved using an alternate provider

- **Groundwater storage anomaly:** GFZ GravIS G3P v1.12, monthly observations through September 2023. Groundwater is inferred from GRACE total storage after subtracting modeled compartments. The map shows an anomaly in mm of equivalent water height, not total aquifer volume.
- **Glacier mass anomaly:** GFZ GravIS G3P v1.12. It shows filtered glacier-mass anomalies as equivalent water height, not total ice-sheet mass. The provider reports significant spatial leakage near coasts.

Both products use an April 2002–December 2020 reference period and 250 km smoothing. Provider-declared June 2005 groundwater data are excluded. Provider images span three repeated longitude worlds in EPSG:4326; the adapter crops the central world and reprojects the imagery to Web Mercator. Colors and legend tick positions are preserved. This process changes the visualization projection and does not generate numerical observations or add geographic detail.

Source and scientific limitations: https://gravis.gfz.de/gws

## Explicit NASA replacements

| Previous variable | Current variable | Provider |
| --- | --- | --- |
| Carbon dioxide | Carbon monoxide | NASA Aqua / AIRS |
| Gravity anomaly | Surface soil moisture | NASA SMAP |
| Surface roughness | Surface albedo | NASA MERRA-2 |
| Land subsidence | Soil temperature | NASA SMAP |
| Tectonic movement | Root-zone soil moisture | NASA SMAP |
| Ice thickness | Snow water equivalent | NASA GIBS / GCOM-W1 AMSR2 |
| Ice sheet elevation | Freeze/thaw state | NASA SMAP |
| Vegetation cover | Gross primary productivity | NASA SMAP |
| Wave height | Sea surface temperature anomaly | NASA GHRSST / MUR |

## Alternate sources considered

- **Carbon dioxide:** NOAA CarbonTracker provides a gridded model record, but its weather-map page returned HTTP 500 during inspection and no ready map source was validated for this app. NASA's gridded AIRS IR CO₂ layer provides an alternate historical record through February 2017. For this interface, the chosen AIRS CO product has a much longer monthly mapped record (2002 onward) and broad gridded coverage. CO is an air-pollution and atmospheric-chemistry variable, not an interchangeable greenhouse-gas measurement. References: https://gml.noaa.gov/ccgg/carbontracker/CT2022/download.php and https://airs.jpl.nasa.gov/map/.
- **Geophysical variables:** the earlier official Australian gravity service returned HTTP 403; available regional ARIA displacement imagery is retained as the Ground displacement entry. USGS plate-boundary imagery would not satisfy a tectonic-movement measurement, and no suitable broad map was validated for the other requested geophysical variables. Replacement soil, reflectivity and root-zone variables address land properties and water/energy exchange rather than pretending to measure deformation.
- **Ice thickness/elevation:** NSIDC BedMachine products exist as downloadable scientific grids; the inspected BAS map service exposed survey-point data rather than a validated broad gridded thickness/elevation map for this interface. Snow water equivalent and freeze/thaw classification were chosen as distinct, explicitly named cryosphere variables. Reference: https://nsidc.org/data/idbmg4/versions/3.
- **Vegetation cover:** MOD44B continuous-cover products exist via NASA extraction/download services, but this app has no validated extraction-to-imagery pipeline for them. SMAP plant productivity offers a different, useful measure of vegetation activity with an existing supported map layer.
- **Wave height:** Copernicus Marine has scientifically appropriate wave-height products, but no compatible map endpoint was validated in this application. The NASA MUR temperature-anomaly layer was selected as another ocean-state variable; it does not represent waves. Reference: https://help.marine.copernicus.eu/en/articles/6175153-how-to-describe-wave-height-period-and-direction-parameters.

These decisions concern usable imagery in this application. They do not imply that the original scientific datasets are unavailable or unimportant. The original requests can be restored when suitable adapters are implemented.

## Verification

- Compared actual overview PNGs for OCO-2 track CO₂, historical AIRS CO₂ and monthly AIRS CO. Nontransparent-pixel fractions are only rendered-image fill metrics, not scientific observation completeness or accuracy scores.
- All 35 catalog sources returned nontransparent images: see map-audit.json for dates, image sizes and request URLs.
- Chrome verified the CO layer and both GFZ maps, their displayed dates, responsive legends and mobile layout, without runtime errors.
- 14 Node tests and 17 Python tests passed, including variable/source completeness, provider dates, GFZ image reprojection, legend positioning and API schemas.

Numerical point trends remain available only for supported NASA POWER variables. Map-source availability does not imply numerical time-series extraction support.
