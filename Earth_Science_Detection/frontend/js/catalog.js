// Variable changes are explicit; a map layer never implies numerical extraction.
export const systems = {
  "atmosphere": {
    "name": "Atmosphere",
    "index": 1,
    "variables": [
      {
        "id": "T2M",
        "name": "Air temperature",
        "unit": "°C",
        "layer": "MERRA2_2m_Air_Temperature_Monthly",
        "provider": "MERRA-2",
        "description": "Air temperature at 2 meters. Map: monthly MERRA-2; point data: daily NASA POWER.",
        "point": true,
        "static": false,
        "imagery": "Air temperature",
        "legend": "https://gibs.earthdata.nasa.gov/legends/MERRA2_2m_Air_Temperature_Monthly_H.png",
        "legendTitle": "Air temperature · °C",
        "monthly": true,
        "coverage": "1980-01-01/2023-11-01/P1M,2024-02-01/2024-04-01/P1M,2024-06-01/2026-08-01/P1M"
      },
      {
        "id": "PS",
        "name": "Atmospheric pressure",
        "unit": "kPa",
        "layer": "MERRA2_Surface_Pressure_Monthly",
        "provider": "MERRA-2",
        "description": "Surface pressure. Map and POWER point data preserve their own native units; see provider legend.",
        "point": true,
        "static": false,
        "imagery": "Atmospheric pressure",
        "legend": "https://gibs.earthdata.nasa.gov/legends/MERRA2_Surface_Pressure_Monthly_H.png",
        "legendTitle": "Atmospheric pressure · kPa",
        "monthly": true,
        "coverage": "1980-01-01/2026-08-01/P1M"
      },
      {
        "id": "PRECTOTCORR",
        "name": "Precipitation",
        "unit": "mm/day",
        "layer": "IMERG_Precipitation_Rate",
        "provider": "GPM / IMERG",
        "description": "Map: satellite precipitation rate; point data: POWER corrected precipitation. These are different products.",
        "point": true,
        "static": false,
        "imagery": "Precipitation",
        "legend": "https://gibs.earthdata.nasa.gov/legends/GPM_Precipitation_Rate_H.png",
        "legendTitle": "Precipitation · mm/day",
        "monthly": false,
        "coverage": "2000-06-01/2025-10-22/P1D,2025-10-30/2026-02-02/P1D,2026-02-04/2026-02-09/P1D,2026-02-12/2026-05-24/P1D,2026-05-27/2026-11-13/P1D"
      },
      {
        "id": "TQV",
        "name": "Water vapor",
        "unit": "kg/m²",
        "layer": "MERRA2_Total_Precipitable_Water_Vapor_Monthly",
        "provider": "MERRA-2",
        "description": "Total column precipitable water, not relative humidity. Point data: NASA POWER.",
        "point": true,
        "static": false,
        "imagery": "Water vapor",
        "legend": "https://gibs.earthdata.nasa.gov/legends/MERRA2_Total_Precipitable_Water_Vapor_Monthly_H.png",
        "legendTitle": "Water vapor · cm",
        "monthly": true,
        "coverage": "1980-01-01/2026-08-01/P1M"
      },
      {
        "id": "OZONE",
        "name": "Total-column ozone",
        "unit": "DU",
        "layer": "KNMI_MSR2_Total_Column_Ozone",
        "provider": "KNMI / TEMIS MSR2",
        "description": "Monthly total-column ozone in Dobson units from KNMI multi-sensor reanalysis. The map, point values and trends use the same 0.5° archive, available through December 2025. This replaces the imagery-only 50 hPa mixing-ratio product.",
        "point": true,
        "static": false,
        "imagery": "Ozone concentration",
        "legend": null,
        "legendTitle": "Total-column ozone · DU",
        "monthly": true,
        "coverage": "1959-02-01/2025-12-01/P1M",
        "coverageNote": "KNMI MSR2 satellite-constrained reanalysis. Map and point observations measure total-column ozone, not surface ozone. Monthly archive currently ends December 2025.",
        "dataProvider": "KNMI / TEMIS MSR2",
        "dataUrl": "https://temis.pmc.knmi.cloud/protocols/O3global.php",
        "sourceUrl": "https://temis.pmc.knmi.cloud/protocols/O3global.php",
        "image": "/api/maps/ozone/{date}.png",
        "dataStart": "1981-01-01",
        "dataEnd": "2025-12-31",
        "dataResolution": "monthly",
        "legendContinuous": true,
        "legendUnit": "Total-column ozone · Dobson units (DU)",
        "legendStops": [
          {
            "label": "150",
            "color": "#323285"
          },
          {
            "label": "200",
            "color": "#327bb7"
          },
          {
            "label": "250",
            "color": "#51bcb7"
          },
          {
            "label": "300",
            "color": "#96d16a"
          },
          {
            "label": "350",
            "color": "#f5e75b"
          },
          {
            "label": "400",
            "color": "#f79b45"
          },
          {
            "label": "450",
            "color": "#c94b54"
          },
          {
            "label": "500",
            "color": "#813985"
          }
        ],
        "legendTicks": [
          {
            "label": "150",
            "position": 0.0
          },
          {
            "label": "250",
            "position": 0.2857142857142857
          },
          {
            "label": "350",
            "position": 0.5714285714285714
          },
          {
            "label": "450",
            "position": 0.8571428571428571
          },
          {
            "label": "500",
            "position": 1.0
          }
        ]
      },
      {
        "id": "CO",
        "name": "Carbon monoxide",
        "unit": "ppbv",
        "layer": "AIRS_L3_Carbon_Monoxide_500hPa_Volume_Mixing_Ratio_Monthly_Day",
        "provider": "NASA Aqua / AIRS",
        "description": "Monthly daytime carbon monoxide mixing ratio at 500 hPa, not surface air quality. This broad gridded pollution product replaces the sparse OCO-2 carbon-dioxide tracks; CO and CO₂ are different gases.",
        "point": false,
        "static": false,
        "imagery": "Carbon monoxide",
        "legend": "https://gibs.earthdata.nasa.gov/legends/AIRS_Carbon_Monoxide_Volume_Mixing_Ratio_H.png",
        "legendTitle": "Carbon monoxide · see provider units",
        "monthly": true,
        "coverage": "2002-09-01/2025-04-01/P1M,2025-07-01/2026-09-01/P1M",
        "sourceUrl": "https://gibs.earthdata.nasa.gov/wms/epsg3857/best/?request=GetMetadata&layer=AIRS_L3_Carbon_Monoxide_500hPa_Volume_Mixing_Ratio_Monthly_Day",
        "coverageNote": "Monthly daytime carbon monoxide mixing ratio at 500 hPa, not surface air quality. This broad gridded pollution product replaces the sparse OCO-2 carbon-dioxide tracks; CO and CO₂ are different gases."
      },
      {
        "id": "CH4",
        "name": "Methane",
        "unit": "ppbv",
        "layer": "AIRS_L3_Methane_400hPa_Volume_Mixing_Ratio_Monthly_Day",
        "provider": "Aqua / AIRS",
        "description": "Methane mixing ratio at 400 hPa, daytime monthly product; not surface methane. Point extraction is not connected.",
        "point": false,
        "static": false,
        "imagery": "Methane",
        "legend": "https://gibs.earthdata.nasa.gov/legends/AIRS_Methane_Volume_Mixing_Ratio_H.png",
        "legendTitle": "Methane · ppbv",
        "monthly": true,
        "coverage": "2002-09-01/2025-04-01/P1M,2025-07-01/2026-09-01/P1M"
      },
      {
        "id": "ALLSKY_SFC_SW_DWN",
        "name": "Solar radiation",
        "unit": "MJ/m²/day",
        "layer": "CERES_Combined_Surface_Shortwave_Flux_Down_All_Sky_Monthly",
        "provider": "CERES",
        "description": "Map: surface shortwave downward flux; POWER returns daily solar energy in its native units.",
        "point": true,
        "static": false,
        "imagery": "Solar radiation",
        "legend": "https://gibs.earthdata.nasa.gov/legends/CERES_Combined_Surface_Shortwave_Flux_Diffuse_H.png",
        "legendTitle": "Solar radiation · MJ/m²/day",
        "monthly": true,
        "coverage": "2002-07-01/2021-07-01/P1M"
      }
    ]
  },
  "geosphere": {
    "name": "Geosphere",
    "index": 2,
    "variables": [
      {
        "id": "ELEVATION",
        "name": "Surface elevation",
        "unit": "m",
        "layer": "ASTER_GDEM_Color_Shaded_Relief",
        "provider": "ASTER GDEM",
        "description": "Static terrain reference. Numerical value: NASA SRTM at approximately 90 m resolution, February 2000 reference, excluding polar regions. Map relief: ASTER. A single reference cannot support a temporal trend.",
        "point": true,
        "static": true,
        "imagery": "Surface elevation",
        "legend": null,
        "legendTitle": "Surface elevation · m",
        "monthly": false,
        "coverage": "",
        "dataProvider": "NASA SRTM · Open Topo Data",
        "dataUrl": "https://www.opentopodata.org/datasets/srtm/"
      },
      {
        "id": "SURFACE_MOISTURE",
        "name": "Surface soil moisture",
        "unit": "m³/m³",
        "layer": "SMAP_L4_Analyzed_Surface_Soil_Moisture",
        "provider": "NASA SMAP",
        "description": "Numerical history: daily ERA5-Land volumetric moisture at 0–7 cm. Map: SMAP L4 at 0–5 cm. The sources and surface-layer depths differ; both report m³/m³. No extraction queue is required.",
        "point": true,
        "static": false,
        "imagery": "Surface soil moisture",
        "legend": "https://gibs.earthdata.nasa.gov/legends/SMAP_Analyzed_Soil_Moisture_H.png",
        "legendTitle": "Surface soil moisture · see provider units",
        "monthly": false,
        "coverage": "2015-03-31/2025-10-09/P1D,2025-12-12/2026-03-16/P1D,2026-03-18/2026-05-10/P1D,2026-05-12/2026-05-16/P1D,2026-05-19/2026-08-09/P1D,2026-08-16/2026-08-30/P1D,2026-09-01/2026-11-06/P1D,2026-11-08/2026-11-10/P1D",
        "sourceUrl": "https://gibs.earthdata.nasa.gov/wms/epsg3857/best/?request=GetMetadata&layer=SMAP_L4_Analyzed_Surface_Soil_Moisture",
        "coverageNote": "Surface-layer soil moisture from a satellite-constrained land model. Ocean pixels are outside the product’s land domain.",
        "dataProvider": "ERA5-Land · Open-Meteo",
        "dataStart": "2015-03-31",
        "dataResolution": "daily",
        "dataUrl": "https://open-meteo.com/en/docs/historical-weather-api"
      },
      {
        "id": "DISPLACEMENT",
        "name": "Ground displacement",
        "unit": "m",
        "layer": "2302_opera_surf_disp",
        "provider": "NASA JPL / ARIA",
        "description": "Regional line-of-sight displacement for the February 2023 Türkiye earthquakes. This is an event map, not current worldwide ground motion.",
        "point": false,
        "static": true,
        "imagery": "Ground displacement",
        "legend": null,
        "legendTitle": "Ground displacement",
        "monthly": false,
        "coverage": "",
        "endpoint": "https://gis.earthdata.nasa.gov/portal/services/DISASTERS_202302_EARTHQUAKE_TURKIYE/2302_opera_surf_disp/ImageServer/WMSServer",
        "sourceUrl": "https://gis.earthdata.nasa.gov/portal/home/item.html?id=36ef72730c214b0e889b857535975f9a",
        "view": {
          "center": [
            36.7,
            37.2
          ],
          "zoom": 6
        },
        "coverageNote": "Regional event product: February 2023 Türkiye earthquakes. No displacement data are shown outside this study area."
      },
      {
        "id": "SOIL",
        "name": "Soil composition",
        "unit": "g/kg",
        "layer": "clay_0-5cm_mean",
        "provider": "ISRIC / SoilGrids",
        "description": "Static predicted clay content in the upper 0–5 cm, in g/kg. Map and one-pixel scientific value use the same SoilGrids coverage. Urban/water and excluded pixels may be masked. A static prediction has no temporal trend.",
        "point": true,
        "static": true,
        "imagery": "Soil composition",
        "legend": "https://maps.isric.org/mapserv?map=/map/clay.map&version=1.3.0&service=WMS&request=GetLegendGraphic&sld_version=1.1.0&layer=clay_0-5cm_mean&format=image/png&STYLE=default",
        "legendTitle": "Soil composition",
        "monthly": false,
        "coverage": "",
        "endpoint": "https://maps.isric.org/mapserv?map=/map/clay.map",
        "sourceUrl": "https://docs.isric.org/globaldata/soilgrids/index.html",
        "coverageNote": "SoilGrids modeled clay content at 0–5 cm. Blank areas have no mapped prediction.",
        "legendStops": [
          {
            "label": "0",
            "color": "#f2dac1"
          },
          {
            "label": "7",
            "color": "#f2dac1"
          },
          {
            "label": "32",
            "color": "#eed2b6"
          },
          {
            "label": "58",
            "color": "#ebcbab"
          },
          {
            "label": "83",
            "color": "#e7c4a0"
          },
          {
            "label": "109",
            "color": "#e3bc96"
          },
          {
            "label": "134",
            "color": "#e0b58b"
          },
          {
            "label": "160",
            "color": "#dcae80"
          },
          {
            "label": "185",
            "color": "#d8a775"
          },
          {
            "label": "211",
            "color": "#d49f6b"
          },
          {
            "label": "236",
            "color": "#d19860"
          },
          {
            "label": "262",
            "color": "#cd9155"
          },
          {
            "label": "288",
            "color": "#c98c50"
          },
          {
            "label": "313",
            "color": "#c5894d"
          },
          {
            "label": "339",
            "color": "#c1854a"
          },
          {
            "label": "364",
            "color": "#bd8247"
          },
          {
            "label": "390",
            "color": "#b97e44"
          },
          {
            "label": "415",
            "color": "#b47b41"
          },
          {
            "label": "441",
            "color": "#b0773e"
          },
          {
            "label": "466",
            "color": "#ac743b"
          },
          {
            "label": "492",
            "color": "#a87038"
          },
          {
            "label": "517",
            "color": "#a36c35"
          },
          {
            "label": "543",
            "color": "#9f6832"
          },
          {
            "label": "569",
            "color": "#9b652f"
          },
          {
            "label": "594",
            "color": "#97612c"
          },
          {
            "label": "620",
            "color": "#935e29"
          },
          {
            "label": "645",
            "color": "#8f5a26"
          },
          {
            "label": "671",
            "color": "#8b5723"
          },
          {
            "label": "696",
            "color": "#875320"
          },
          {
            "label": "722",
            "color": "#83501d"
          },
          {
            "label": "747",
            "color": "#7e4c1a"
          },
          {
            "label": "773",
            "color": "#7a4917"
          },
          {
            "label": "799",
            "color": "#764615"
          }
        ],
        "legendUnit": "Clay content · g/kg · depth 0–5 cm",
        "dataProvider": "ISRIC SoilGrids 2.0",
        "dataUrl": "https://www.isric.org/explore/soilgrids"
      },
      {
        "id": "ALBEDO",
        "name": "Surface albedo",
        "unit": "dimensionless",
        "layer": "MERRA2_Surface_Albedo_Monthly",
        "provider": "NASA MERRA-2",
        "description": "Fraction of incoming sunlight reflected by the surface. Daily numerical series: POWER all-sky surface albedo. Imagery: monthly MERRA-2, a different source product.",
        "point": true,
        "static": false,
        "imagery": "Surface albedo",
        "legend": "https://gibs.earthdata.nasa.gov/legends/MERRA2_Surface_Albedo_Monthly_H.png",
        "legendTitle": "Surface albedo · see provider units",
        "monthly": true,
        "coverage": "1980-01-01/2026-08-01/P1M",
        "sourceUrl": "https://gibs.earthdata.nasa.gov/wms/epsg3857/best/?request=GetMetadata&layer=MERRA2_Surface_Albedo_Monthly",
        "coverageNote": "Monthly modeled surface reflectivity: the fraction of incoming sunlight reflected by the surface. This is not surface roughness.",
        "dataProvider": "NASA POWER"
      },
      {
        "id": "SOIL_TEMPERATURE",
        "name": "Soil temperature",
        "unit": "°C",
        "layer": "SMAP_L4_Soil_Temperature_Layer_1",
        "provider": "NASA SMAP",
        "description": "Modeled upper-layer soil temperature. Numerical values: NASA POWER TSOIL1 (°C), retrieved directly. Imagery: SMAP L4 upper-layer temperature; source grids and layers differ.",
        "point": true,
        "static": false,
        "imagery": "Soil temperature",
        "legend": "https://gibs.earthdata.nasa.gov/legends/SMAP_Soil_Temperature_Layer_H.png",
        "legendTitle": "Soil temperature · see provider units",
        "monthly": false,
        "coverage": "2015-03-31/2025-10-09/P1D,2025-12-12/2026-03-16/P1D,2026-03-18/2026-05-10/P1D,2026-05-12/2026-05-16/P1D,2026-05-19/2026-08-09/P1D,2026-08-16/2026-08-30/P1D,2026-09-01/2026-11-06/P1D,2026-11-08/2026-11-10/P1D",
        "sourceUrl": "https://gibs.earthdata.nasa.gov/wms/epsg3857/best/?request=GetMetadata&layer=SMAP_L4_Soil_Temperature_Layer_1",
        "coverageNote": "Modeled upper-layer soil temperature from the SMAP land model, not atmospheric temperature or land subsidence.",
        "dataProvider": "NASA POWER",
        "dataStart": "2015-03-31",
        "dataResolution": "daily"
      },
      {
        "id": "ROOT_MOISTURE",
        "name": "Root-zone soil moisture",
        "unit": "m³/m³",
        "layer": "SMAP_L4_Analyzed_Root_Zone_Soil_Moisture",
        "provider": "NASA SMAP",
        "description": "Numerical history: daily ERA5-Land volumetric root-zone moisture at 0–100 cm. Map: SMAP L4 modeled root-zone moisture. These use different land models and grids, with the same physical units.",
        "point": true,
        "static": false,
        "imagery": "Root-zone soil moisture",
        "legend": "https://gibs.earthdata.nasa.gov/legends/SMAP_Analyzed_Soil_Moisture_H.png",
        "legendTitle": "Root-zone soil moisture · see provider units",
        "monthly": false,
        "coverage": "2015-03-31/2025-10-09/P1D,2025-12-12/2026-03-16/P1D,2026-03-18/2026-05-10/P1D,2026-05-12/2026-05-16/P1D,2026-05-19/2026-08-09/P1D,2026-08-16/2026-08-30/P1D,2026-09-01/2026-11-06/P1D,2026-11-08/2026-11-10/P1D",
        "sourceUrl": "https://gibs.earthdata.nasa.gov/wms/epsg3857/best/?request=GetMetadata&layer=SMAP_L4_Analyzed_Root_Zone_Soil_Moisture",
        "coverageNote": "Satellite-constrained modeled moisture deeper in the soil, where plant roots draw water. This is a land-water measurement, not tectonic motion.",
        "dataProvider": "ERA5-Land · Open-Meteo",
        "dataStart": "2015-03-31",
        "dataResolution": "daily",
        "dataUrl": "https://open-meteo.com/en/docs/historical-weather-api"
      }
    ]
  },
  "cryosphere": {
    "name": "Cryosphere",
    "index": 5,
    "variables": [
      {
        "id": "SEA_ICE",
        "name": "Sea ice concentration",
        "unit": "%",
        "layer": "GHRSST_L4_MUR_Sea_Ice_Concentration",
        "provider": "GHRSST / MUR",
        "description": "Numerical extraction is not connected for this variable.",
        "point": true,
        "static": false,
        "imagery": "Sea ice concentration",
        "legend": "https://gibs.earthdata.nasa.gov/legends/GHRSST_Sea_Ice_Concentration_H.png",
        "legendTitle": "Sea ice concentration · %",
        "monthly": false,
        "coverage": "2002-06-01/2021-02-19/P1D,2021-02-22/2022-11-08/P1D,2022-11-10/2023-02-01/P1D,2023-02-04/2023-04-21/P1D,2023-04-23/2024-07-01/P1D,2024-07-03/2026-11-13/P1D",
        "dataProvider": "NASA JPL MUR · NOAA ERDDAP",
        "dataStart": "2002-06-01",
        "dataResolution": "daily"
      },
      {
        "id": "SWE",
        "name": "Snow water equivalent",
        "unit": "mm water equivalent",
        "layer": "SMAP_L4_Snow_Mass",
        "provider": "NASA SMAP L4",
        "description": "SMAP L4 modeled snow water equivalent over land, excluding permanent ice and open water. Point data: 3-hourly SPL4SMGP.008; map: daily snow mass. One kg/m² equals one mm of water.",
        "point": true,
        "static": false,
        "imagery": "Snow water equivalent",
        "legend": "https://gibs.earthdata.nasa.gov/legends/SMAP_Snow_Mass_H.png",
        "legendTitle": "Snow water equivalent · mm water equivalent",
        "monthly": false,
        "coverage": "2015-03-31/2025-08-02/P1D,2025-08-04/2025-10-09/P1D,2025-12-12/2025-12-30/P1D,2026-01-01/2026-03-16/P1D,2026-03-18/2026-05-16/P1D,2026-05-19/2026-08-09/P1D,2026-08-11/2026-08-11/P1D,2026-08-15/2026-08-30/P1D,2026-09-01/2026-11-10/P1D",
        "sourceUrl": "https://gibs.earthdata.nasa.gov/wms/epsg3857/best/?request=GetMetadata&layer=AMSRU2_Snow_Water_Equivalent_Monthly",
        "coverageNote": "Ongoing SMAP L4 snow mass replaces the discontinued AMSR2 monthly imagery. Land and permanent-ice masks remain scientifically necessary.",
        "view": {
          "center": [
            15,
            60
          ],
          "zoom": 1.7
        },
        "dataProvider": "NASA AppEEARS",
        "dataStart": "2015-03-31",
        "dataResolution": "daily"
      },
      {
        "id": "FREEZE_THAW",
        "name": "Freeze/thaw state",
        "unit": "categories",
        "layer": "SMAP_L3_Passive_Enhanced_Day_Freeze_Thaw",
        "provider": "NASA SMAP",
        "description": "Morning land-surface freeze/thaw classification. It is categorical, not ice-sheet elevation; unmapped areas are outside the valid retrieval domain.",
        "point": true,
        "static": false,
        "imagery": "Freeze/thaw state",
        "legend": "https://gibs.earthdata.nasa.gov/legends/SMAP_Freeze_Thaw_H.png",
        "legendTitle": "Freeze/thaw state · see provider units",
        "monthly": false,
        "coverage": "2015-03-31/2015-05-12/P1D,2015-05-14/2015-12-15/P1D,2015-12-17/2016-04-30/P1D,2016-05-02/2016-09-26/P1D,2016-09-28/2019-06-19/P1D,2019-07-23/2022-08-06/P1D,2022-10-07/2022-11-16/P1D,2022-11-18/2025-03-17/P1D,2025-03-19/2026-09-02/P1D,2026-09-04/2026-09-19/P1D,2026-09-21/2026-09-29/P1D,2026-10-01/2026-10-17/P1D,2026-10-19/2026-10-25/P1D,2026-10-27/2026-11-01/P1D,2026-11-03/2026-11-11/P1D",
        "sourceUrl": "https://gibs.earthdata.nasa.gov/wms/epsg3857/best/?request=GetMetadata&layer=SMAP_L3_Passive_Enhanced_Day_Freeze_Thaw",
        "coverageNote": "Morning land-surface freeze/thaw classification. It is categorical, not ice-sheet elevation; unmapped areas are outside the valid retrieval domain.",
        "view": {
          "center": [
            15,
            60
          ],
          "zoom": 1.7
        },
        "dataProvider": "NASA AppEEARS",
        "dataStart": "2015-03-31",
        "dataResolution": "daily"
      },
      {
        "id": "ICE_MASS",
        "name": "Glacier mass anomaly",
        "unit": "mm water equivalent",
        "layer": "G3P_glac",
        "provider": "GFZ / GravIS G3P v1.12",
        "description": "Monthly filtered glacier-mass anomaly from the GFZ G3P prototype, shown as equivalent water height. It is not total ice-sheet mass; spatial smoothing can leak signals near coasts. Numerical history is the provider’s mean for the containing aquifer/basin/climate region, not a point measurement. Record ends September 2023.",
        "point": true,
        "static": false,
        "imagery": "Glacier mass anomaly",
        "legend": "https://gravis.gfz.de/legendy/G3P/glac/50",
        "legendTitle": "Glacier mass anomaly · mm water equivalent",
        "monthly": true,
        "coverage": "",
        "image": "/api/maps/gravis/glac/{date}.png",
        "gravisField": "glac",
        "sourceUrl": "https://gravis.gfz.de/gws",
        "availableDates": [
          "2002-04-16",
          "2002-05-16",
          "2002-06-16",
          "2002-07-16",
          "2002-08-16",
          "2002-09-16",
          "2002-10-16",
          "2002-11-16",
          "2002-12-16",
          "2003-01-16",
          "2003-02-16",
          "2003-03-16",
          "2003-04-16",
          "2003-05-16",
          "2003-06-16",
          "2003-07-16",
          "2003-08-16",
          "2003-09-16",
          "2003-10-16",
          "2003-11-16",
          "2003-12-16",
          "2004-01-16",
          "2004-02-16",
          "2004-03-16",
          "2004-04-16",
          "2004-05-16",
          "2004-06-16",
          "2004-07-16",
          "2004-08-16",
          "2004-09-16",
          "2004-10-16",
          "2004-11-16",
          "2004-12-16",
          "2005-01-16",
          "2005-02-16",
          "2005-03-16",
          "2005-04-16",
          "2005-05-16",
          "2005-06-16",
          "2005-07-16",
          "2005-08-16",
          "2005-09-16",
          "2005-10-16",
          "2005-11-16",
          "2005-12-16",
          "2006-01-16",
          "2006-02-16",
          "2006-03-16",
          "2006-04-16",
          "2006-05-16",
          "2006-06-16",
          "2006-07-16",
          "2006-08-16",
          "2006-09-16",
          "2006-10-16",
          "2006-11-16",
          "2006-12-16",
          "2007-01-16",
          "2007-02-16",
          "2007-03-16",
          "2007-04-16",
          "2007-05-16",
          "2007-06-16",
          "2007-07-16",
          "2007-08-16",
          "2007-09-16",
          "2007-10-16",
          "2007-11-16",
          "2007-12-16",
          "2008-01-16",
          "2008-02-16",
          "2008-03-16",
          "2008-04-16",
          "2008-05-16",
          "2008-06-16",
          "2008-07-16",
          "2008-08-16",
          "2008-09-16",
          "2008-10-16",
          "2008-11-16",
          "2008-12-16",
          "2009-01-16",
          "2009-02-16",
          "2009-03-16",
          "2009-04-16",
          "2009-05-16",
          "2009-06-16",
          "2009-07-16",
          "2009-08-16",
          "2009-09-16",
          "2009-10-16",
          "2009-11-16",
          "2009-12-16",
          "2010-01-16",
          "2010-02-16",
          "2010-03-16",
          "2010-04-16",
          "2010-05-16",
          "2010-06-16",
          "2010-07-16",
          "2010-08-16",
          "2010-09-16",
          "2010-10-16",
          "2010-11-16",
          "2010-12-16",
          "2011-01-16",
          "2011-02-16",
          "2011-03-16",
          "2011-04-16",
          "2011-05-16",
          "2011-06-16",
          "2011-07-16",
          "2011-08-16",
          "2011-09-16",
          "2011-10-16",
          "2011-11-16",
          "2011-12-16",
          "2012-01-16",
          "2012-02-16",
          "2012-03-16",
          "2012-04-16",
          "2012-05-16",
          "2012-06-16",
          "2012-07-16",
          "2012-08-16",
          "2012-09-16",
          "2012-10-16",
          "2012-11-16",
          "2012-12-16",
          "2013-01-16",
          "2013-02-16",
          "2013-03-16",
          "2013-04-16",
          "2013-05-16",
          "2013-06-16",
          "2013-07-16",
          "2013-08-16",
          "2013-09-16",
          "2013-10-16",
          "2013-11-16",
          "2013-12-16",
          "2014-01-16",
          "2014-02-16",
          "2014-03-16",
          "2014-04-16",
          "2014-05-16",
          "2014-06-16",
          "2014-07-16",
          "2014-08-16",
          "2014-09-16",
          "2014-10-16",
          "2014-11-16",
          "2014-12-16",
          "2015-01-16",
          "2015-02-16",
          "2015-03-16",
          "2015-04-16",
          "2015-05-16",
          "2015-06-16",
          "2015-07-16",
          "2015-08-16",
          "2015-09-16",
          "2015-10-16",
          "2015-11-16",
          "2015-12-16",
          "2016-01-16",
          "2016-02-16",
          "2016-03-16",
          "2016-04-16",
          "2016-05-16",
          "2016-06-16",
          "2016-07-16",
          "2016-08-16",
          "2016-09-16",
          "2016-10-16",
          "2016-11-16",
          "2016-12-16",
          "2017-01-16",
          "2017-02-16",
          "2017-03-16",
          "2017-04-16",
          "2017-05-16",
          "2017-06-16",
          "2017-07-16",
          "2017-08-16",
          "2017-09-16",
          "2017-10-16",
          "2017-11-16",
          "2017-12-16",
          "2018-01-16",
          "2018-02-16",
          "2018-03-16",
          "2018-04-16",
          "2018-05-16",
          "2018-06-16",
          "2018-07-16",
          "2018-08-16",
          "2018-09-16",
          "2018-10-16",
          "2018-11-16",
          "2018-12-16",
          "2019-01-16",
          "2019-02-16",
          "2019-03-16",
          "2019-04-16",
          "2019-05-16",
          "2019-06-16",
          "2019-07-16",
          "2019-08-16",
          "2019-09-16",
          "2019-10-16",
          "2019-11-16",
          "2019-12-16",
          "2020-01-16",
          "2020-02-16",
          "2020-03-16",
          "2020-04-16",
          "2020-05-16",
          "2020-06-16",
          "2020-07-16",
          "2020-08-16",
          "2020-09-16",
          "2020-10-16",
          "2020-11-16",
          "2020-12-16",
          "2021-01-16",
          "2021-02-16",
          "2021-03-16",
          "2021-04-16",
          "2021-05-16",
          "2021-06-16",
          "2021-07-16",
          "2021-08-16",
          "2021-09-16",
          "2021-10-16",
          "2021-11-16",
          "2021-12-16",
          "2022-01-16",
          "2022-02-16",
          "2022-03-16",
          "2022-04-16",
          "2022-05-16",
          "2022-06-16",
          "2022-07-16",
          "2022-08-16",
          "2022-09-16",
          "2022-10-16",
          "2022-11-16",
          "2022-12-16",
          "2023-01-16",
          "2023-02-16",
          "2023-03-16",
          "2023-04-16",
          "2023-05-16",
          "2023-06-16",
          "2023-07-16",
          "2023-08-16",
          "2023-09-16"
        ],
        "coverageNote": "GFZ G3P prototype monthly anomalies, baseline April 2002–December 2020; 250 km smoothing. Monthly filtered glacier-mass anomaly from the GFZ G3P prototype, shown as equivalent water height. It is not total ice-sheet mass; spatial smoothing can leak signals near coasts.",
        "legendStops": [
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(115,4,33)"
          },
          {
            "label": "",
            "color": "rgb(128,8,35)"
          },
          {
            "label": "",
            "color": "rgb(140,12,37)"
          },
          {
            "label": "",
            "color": "rgb(153,16,39)"
          },
          {
            "label": "",
            "color": "rgb(166,20,41)"
          },
          {
            "label": "",
            "color": "rgb(178,24,43)"
          },
          {
            "label": "",
            "color": "rgb(184,37,49)"
          },
          {
            "label": "",
            "color": "rgb(191,50,55)"
          },
          {
            "label": "",
            "color": "rgb(197,62,61)"
          },
          {
            "label": "",
            "color": "rgb(203,75,67)"
          },
          {
            "label": "",
            "color": "rgb(210,88,73)"
          },
          {
            "label": "",
            "color": "rgb(216,100,80)"
          },
          {
            "label": "",
            "color": "rgb(221,112,89)"
          },
          {
            "label": "",
            "color": "rgb(226,125,99)"
          },
          {
            "label": "",
            "color": "rgb(231,137,108)"
          },
          {
            "label": "",
            "color": "rgb(237,149,117)"
          },
          {
            "label": "",
            "color": "rgb(242,161,127)"
          },
          {
            "label": "",
            "color": "rgb(245,171,138)"
          },
          {
            "label": "",
            "color": "rgb(246,180,149)"
          },
          {
            "label": "",
            "color": "rgb(248,189,161)"
          },
          {
            "label": "",
            "color": "rgb(249,198,173)"
          },
          {
            "label": "",
            "color": "rgb(251,208,184)"
          },
          {
            "label": "",
            "color": "rgb(252,217,196)"
          },
          {
            "label": "",
            "color": "rgb(252,222,205)"
          },
          {
            "label": "",
            "color": "rgb(251,227,213)"
          },
          {
            "label": "",
            "color": "rgb(250,232,221)"
          },
          {
            "label": "",
            "color": "rgb(249,236,229)"
          },
          {
            "label": "",
            "color": "rgb(248,241,237)"
          },
          {
            "label": "",
            "color": "rgb(247,246,246)"
          },
          {
            "label": "",
            "color": "rgb(241,244,245)"
          },
          {
            "label": "",
            "color": "rgb(234,241,244)"
          },
          {
            "label": "",
            "color": "rgb(227,237,243)"
          },
          {
            "label": "",
            "color": "rgb(221,234,242)"
          },
          {
            "label": "",
            "color": "rgb(214,231,240)"
          },
          {
            "label": "",
            "color": "rgb(206,227,239)"
          },
          {
            "label": "",
            "color": "rgb(195,222,236)"
          },
          {
            "label": "",
            "color": "rgb(184,216,233)"
          },
          {
            "label": "",
            "color": "rgb(173,210,229)"
          },
          {
            "label": "",
            "color": "rgb(162,205,226)"
          },
          {
            "label": "",
            "color": "rgb(151,199,223)"
          },
          {
            "label": "",
            "color": "rgb(139,192,219)"
          },
          {
            "label": "",
            "color": "rgb(125,184,215)"
          },
          {
            "label": "",
            "color": "rgb(112,175,210)"
          },
          {
            "label": "",
            "color": "rgb(98,167,205)"
          },
          {
            "label": "",
            "color": "rgb(85,158,201)"
          },
          {
            "label": "",
            "color": "rgb(72,150,196)"
          },
          {
            "label": "",
            "color": "rgb(63,142,192)"
          },
          {
            "label": "",
            "color": "rgb(57,134,188)"
          },
          {
            "label": "",
            "color": "rgb(52,127,184)"
          },
          {
            "label": "",
            "color": "rgb(46,119,180)"
          },
          {
            "label": "",
            "color": "rgb(40,111,177)"
          },
          {
            "label": "",
            "color": "rgb(34,104,173)"
          },
          {
            "label": "",
            "color": "rgb(29,95,162)"
          },
          {
            "label": "",
            "color": "rgb(24,85,149)"
          },
          {
            "label": "",
            "color": "rgb(19,76,136)"
          },
          {
            "label": "",
            "color": "rgb(14,66,123)"
          },
          {
            "label": "",
            "color": "rgb(9,57,110)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          }
        ],
        "legendTicks": [
          {
            "label": "-1000",
            "position": 0.2666666666666667
          },
          {
            "label": "0",
            "position": 0.6
          },
          {
            "label": "1000",
            "position": 0.9333333333333333
          }
        ],
        "legendContinuous": true,
        "legendUnit": "Water-equivalent anomaly · mm",
        "view": {
          "center": [
            -42,
            70
          ],
          "zoom": 2
        },
        "dataProvider": "GFZ G3P · regional mean",
        "dataUrl": "https://gravis.gfz.de/gws",
        "dataStart": "2002-04-01",
        "dataEnd": "2023-09-30",
        "dataResolution": "monthly"
      },
      {
        "id": "GLACIER_VELOCITY",
        "name": "Glacier velocity",
        "unit": "m/year",
        "layer": "ITS_LIVE_velocity_composite",
        "provider": "NASA MEaSUREs / ITS_LIVE",
        "description": "ITS_LIVE published glacier-speed tile composite. This is a reference mosaic, not a measurement on the selected imagery date.",
        "point": false,
        "static": true,
        "imagery": "Glacier velocity",
        "legend": null,
        "legendTitle": "Glacier velocity",
        "monthly": false,
        "coverage": "",
        "tiles": "https://its-live-data.s3.us-west-2.amazonaws.com/vel_web_tiles/3857/{z}/{x}/{y}.png",
        "sourceUrl": "https://nasa-jpl.github.io/itslive-web/",
        "view": {
          "center": [
            -42,
            72
          ],
          "zoom": 2.5
        },
        "minzoom": 1,
        "maxzoom": 10,
        "coverageNote": "ITS_LIVE reference velocity mosaic. Coverage is limited to mapped glaciers; geographic gaps are expected."
      },
      {
        "id": "SNOW",
        "name": "Snow cover",
        "unit": "% land area",
        "layer": "MODIS_Terra_NDSI_Snow_Cover",
        "provider": "MODIS / Terra",
        "description": "Numerical history: daily modeled fraction of land covered by snow from NASA POWER, expressed as percent. Map: MODIS NDSI snow detection, a different observation/index product. Snow-free modeled days can legitimately be zero.",
        "point": true,
        "static": false,
        "imagery": "Snow cover",
        "legend": "https://gibs.earthdata.nasa.gov/legends/MODIS_NDSI_Snow_Cover_H.png",
        "legendTitle": "Snow cover · %",
        "monthly": false,
        "coverage": "2000-02-24/2000-08-06/P1D,2000-08-18/2001-06-15/P1D,2001-07-03/2002-03-19/P1D,2002-03-28/2003-12-16/P1D,2003-12-24/2008-12-20/P1D,2008-12-23/2016-02-18/P1D,2016-02-27/2022-10-10/P1D,2022-10-23/2026-11-15/P1D",
        "dataProvider": "NASA POWER",
        "dataStart": "2001-01-01",
        "dataResolution": "daily"
      },
      {
        "id": "ICE_TEMP",
        "name": "Ice surface temperature",
        "unit": "°C",
        "layer": "MODIS_Terra_L3_Ice_Surface_Temp_Daily_Day",
        "provider": "MODIS / Terra",
        "description": "Numerical extraction is not connected for this variable.",
        "point": false,
        "static": false,
        "imagery": "Ice surface temperature",
        "legend": "https://gibs.earthdata.nasa.gov/legends/MODIS_Ice_Surface_Temp_H.png",
        "legendTitle": "Ice surface temperature · °C",
        "monthly": false,
        "coverage": "2000-02-24/2000-08-05/P1D,2000-08-18/2001-06-15/P1D,2001-07-03/2002-03-19/P1D,2002-03-28/2002-04-14/P1D,2002-04-16/2003-12-16/P1D,2003-12-24/2008-12-20/P1D,2008-12-23/2016-02-18/P1D,2016-02-28/2022-10-10/P1D,2022-10-23/2026-02-08/P1D,2026-02-10/2026-11-13/P1D"
      }
    ]
  },
  "biosphere": {
    "name": "Biosphere",
    "index": 4,
    "variables": [
      {
        "id": "LST",
        "name": "Land surface temperature",
        "unit": "°C",
        "layer": "MODIS_Terra_L3_Land_Surface_Temp_Monthly_Day",
        "provider": "MODIS / Terra",
        "description": "Daytime land surface temperature. Point values: MODIS MOD11A2 8-day native pixel, retrieved directly from NASA ORNL without an extraction queue. Map: MODIS monthly land temperature; its averaging period differs.",
        "point": true,
        "static": false,
        "imagery": "Land surface temperature",
        "legend": "https://gibs.earthdata.nasa.gov/legends/MODIS_Land_Surface_Temp_H.png",
        "legendTitle": "Land surface temperature · °C",
        "monthly": true,
        "coverage": "2000-03-01/2026-10-01/P1M",
        "dataProvider": "NASA ORNL TESViS",
        "dataStart": "2001-01-01",
        "dataResolution": "8-day",
        "dataUrl": "https://modis.ornl.gov/data/modis_webservice.html"
      },
      {
        "id": "NDVI",
        "name": "Vegetation index (NDVI)",
        "unit": "unitless",
        "layer": "MODIS_Terra_L3_NDVI_Monthly",
        "provider": "MODIS / Terra",
        "description": "Vegetation greenness. Point history: MODIS MOD13Q1 16-day, 250 m native pixel from NASA ORNL with pixel-reliability filtering. Map: MODIS monthly NDVI; period and grid differ.",
        "point": true,
        "static": false,
        "imagery": "Vegetation index (NDVI)",
        "legend": "https://gibs.earthdata.nasa.gov/legends/MODIS_L3_NDVI_H.png",
        "legendTitle": "Vegetation index (NDVI) · unitless",
        "monthly": true,
        "coverage": "2000-03-01/2025-03-01/P1M,2025-05-01/2026-10-01/P1M",
        "dataProvider": "NASA ORNL TESViS",
        "dataStart": "2001-01-01",
        "dataResolution": "16-day",
        "dataUrl": "https://modis.ornl.gov/data/modis_webservice.html"
      },
      {
        "id": "GPP",
        "name": "Gross primary productivity",
        "unit": "provider units",
        "layer": "SMAP_L4_Mean_Gross_Primary_Productivity",
        "provider": "NASA SMAP",
        "description": "Gross primary productivity. Numerical history uses MODIS MOD17A2HGF, converted from composite kg C/m² to average g C/m²/day, with quality filtering. Imagery currently uses the SMAP carbon model, a different productivity estimate.",
        "point": true,
        "static": false,
        "imagery": "Gross primary productivity",
        "legend": "https://gibs.earthdata.nasa.gov/legends/SMAP_Mean_Gross_Primary_Productivity_H.png",
        "legendTitle": "Gross primary productivity · see provider units",
        "monthly": false,
        "coverage": "2015-03-31/2025-10-07/P1D,2025-12-12/2025-12-25/P1D,2026-01-01/2026-03-05/P1D,2026-03-18/2026-04-14/P1D,2026-04-18/2026-04-18/P1D,2026-04-20/2026-04-20/P1D,2026-04-22/2026-06-09/P1D,2026-06-12/2026-06-13/P1D,2026-06-15/2026-07-27/P1D,2026-08-01/2026-08-01/P1D,2026-08-07/2026-08-07/P1D,2026-08-11/2026-08-30/P1D,2026-09-01/2026-10-07/P1D,2026-10-09/2026-10-31/P1D",
        "sourceUrl": "https://gibs.earthdata.nasa.gov/wms/epsg3857/best/?request=GetMetadata&layer=SMAP_L4_Mean_Gross_Primary_Productivity",
        "coverageNote": "Modeled carbon uptake by photosynthesis. This measures vegetation activity, not the percentage of ground covered by vegetation.",
        "dataProvider": "NASA ORNL TESViS",
        "dataStart": "2015-03-31",
        "dataResolution": "8-day",
        "dataUrl": "https://modis.ornl.gov/data/modis_webservice.html"
      },
      {
        "id": "BIOMASS",
        "name": "Biomass",
        "unit": "Mg/ha",
        "layer": "GEDI_ISS_L4B_Aboveground_Biomass_Density_Mean_201904-202303",
        "provider": "GEDI",
        "description": "Aboveground biomass density composite, April 2019–March 2023. Not a daily observation.",
        "point": false,
        "static": true,
        "imagery": "Biomass",
        "legend": "https://gibs.earthdata.nasa.gov/legends/GEDI_MU_Color_Index_H.png",
        "legendTitle": "Biomass · Mg/ha",
        "monthly": false,
        "coverage": "2019-04-18/2019-04-18/P1429D"
      },
      {
        "id": "LAND_COVER",
        "name": "Land cover",
        "unit": "categories",
        "layer": "MODIS_Combined_L3_IGBP_Land_Cover_Type_Annual",
        "provider": "MODIS",
        "description": "Annual IGBP land-cover classes, retrieved directly through NASA ORNL. Analysis reports changes between observed categories; class numbers do not have a physical linear slope.",
        "point": true,
        "static": false,
        "imagery": "Land cover",
        "legend": "https://gibs.earthdata.nasa.gov/legends/MODIS_IGBP_Land_Cover_Type_H.png",
        "legendTitle": "Land cover · categories",
        "monthly": false,
        "coverage": "2001-01-01/2024-01-01/P1Y",
        "dataProvider": "NASA ORNL TESViS",
        "dataStart": "2001-01-01",
        "dataResolution": "annual",
        "dataUrl": "https://modis.ornl.gov/data/modis_webservice.html"
      },
      {
        "id": "FIRE",
        "name": "Fire intensity",
        "unit": "MW",
        "layer": "NASA_FIRMS_NOAA20_Detections",
        "provider": "NASA FIRMS · NOAA-20",
        "description": "Actual NOAA-20 VIIRS fire detections from NASA FIRMS. Hover for MW and acquisition time; only displayed detections can be selected. The public feed covers the rolling seven days. The graph uses recorded detections within 750 m of the selected pixel, not an invented continuous fire record.",
        "point": true,
        "static": false,
        "imagery": "Fire intensity",
        "legend": null,
        "legendTitle": "Fire radiative power · MW",
        "monthly": false,
        "coverage": "2026-11-08/2026-11-15/P1D",
        "sourceUrl": "https://firms.modaps.eosdis.nasa.gov/active_fire/",
        "coverageNote": "Click a displayed NASA FIRMS detection to retrieve radiative power. Hover reveals its value and acquisition time. No detection does not mean zero fire risk.",
        "legendUnit": "Detected-pixel fire radiative power · MW",
        "legendContinuous": true,
        "legendTickLabels": [
          "0",
          "50",
          "100",
          "150+"
        ],
        "legendStops": [
          {
            "label": "0",
            "color": "#ffed8a"
          },
          {
            "label": "10",
            "color": "#fec44f"
          },
          {
            "label": "50",
            "color": "#fe9929"
          },
          {
            "label": "100",
            "color": "#ec7014"
          },
          {
            "label": "150",
            "color": "#cc4c02"
          }
        ],
        "dataProvider": "NASA FIRMS · NOAA-20",
        "dataUrl": "https://firms.modaps.eosdis.nasa.gov/active_fire/",
        "points": "/api/maps/fire/{date}.geojson",
        "dataStart": "2026-11-08",
        "dataEnd": "2026-11-15",
        "dataResolution": "irregular",
        "legendTicks": [
          {
            "label": "0",
            "position": 0.0
          },
          {
            "label": "50",
            "position": 0.3333333333333333
          },
          {
            "label": "100",
            "position": 0.6666666666666666
          },
          {
            "label": "≥150",
            "position": 1.0
          }
        ]
      }
    ]
  },
  "hydrosphere": {
    "name": "Hydrosphere",
    "index": 3,
    "variables": [
      {
        "id": "SST",
        "name": "Sea surface temperature",
        "unit": "°C",
        "layer": "GHRSST_L4_MUR_Sea_Surface_Temperature",
        "provider": "GHRSST / MUR",
        "description": "Daily sea temperature history from NASA Harmony MUR25 v4.2 (0.25°). The map uses finer MUR v4.1 imagery. Select an ocean point; masked or land cells have no temperature value.",
        "point": true,
        "static": false,
        "imagery": "Sea surface temperature",
        "legend": "https://gibs.earthdata.nasa.gov/legends/GHRSST_Sea_Surface_Temperature_H.png",
        "legendTitle": "Sea surface temperature · °C",
        "monthly": false,
        "coverage": "2002-06-01/2021-02-19/P1D,2021-02-22/2022-11-08/P1D,2022-11-10/2023-02-01/P1D,2023-02-04/2023-04-21/P1D,2023-04-23/2024-07-01/P1D,2024-07-03/2026-11-13/P1D",
        "dataProvider": "NASA JPL MUR25 v4.2 · Harmony",
        "dataStart": "2002-09-01",
        "dataUrl": "https://podaac.jpl.nasa.gov/dataset/MUR25-JPL-L4-GLOB-v04.2",
        "dataResolution": "daily"
      },
      {
        "id": "SALINITY",
        "name": "Sea surface salinity",
        "unit": "PSU",
        "layer": "NOAA_SALINITY",
        "provider": "NOAA CoastWatch",
        "description": "Sea surface salinity from SMOS 3-day composites via NOAA. Map and numerical history now use the same source, replacing the previous SMAP imagery. Ocean-only; coastal and polar retrieval masks remain.",
        "point": true,
        "static": false,
        "imagery": "Sea surface salinity",
        "legend": "/api/maps/ocean/SALINITY/legend.png",
        "legendTitle": "Sea surface salinity · PSU",
        "monthly": false,
        "coverage": "2010-06-03/2026-11-09/P3D",
        "dataProvider": "NOAA CoastWatch",
        "dataUrl": "https://coastwatch.pfeg.noaa.gov/erddap/",
        "sourceUrl": "https://coastwatch.pfeg.noaa.gov/erddap/",
        "image": "/api/maps/ocean/SALINITY/{date}.png",
        "dataStart": "2010-06-03",
        "dataEnd": "2026-11-09",
        "dataResolution": "daily",
        "coverageNote": "NOAA CoastWatch numerical product. Land and excluded coastal or polar pixels remain masked; unavailable pixels are not zero."
      },
      {
        "id": "SEA_LEVEL",
        "name": "Sea-level anomaly",
        "unit": "m",
        "layer": "NOAA_SEA_LEVEL",
        "provider": "NOAA CoastWatch",
        "description": "NOAA experimental satellite-altimetry sea-level anomaly (m), from 2017 onward. Map and numerical history use the same source. This is not absolute ocean depth.",
        "point": true,
        "static": false,
        "imagery": "Sea level",
        "legend": "/api/maps/ocean/SEA_LEVEL/legend.png",
        "legendTitle": "Sea level · m",
        "monthly": false,
        "coverage": "2017-02-13/2026-09-28/P1D",
        "dataProvider": "NOAA CoastWatch",
        "dataUrl": "https://coastwatch.pfeg.noaa.gov/erddap/",
        "sourceUrl": "https://coastwatch.pfeg.noaa.gov/erddap/",
        "image": "/api/maps/ocean/SEA_LEVEL/{date}.png",
        "dataStart": "2017-02-13",
        "dataEnd": "2026-09-28",
        "dataResolution": "daily",
        "coverageNote": "NOAA CoastWatch numerical product. Land and excluded coastal or polar pixels remain masked; unavailable pixels are not zero."
      },
      {
        "id": "CURRENTS",
        "name": "Eastward geostrophic current",
        "unit": "m/s",
        "layer": "NOAA_CURRENTS",
        "provider": "NOAA CoastWatch",
        "description": "Eastward geostrophic velocity from NOAA experimental satellite altimetry. Both map and series use this source, replacing the retired OSCAR map. This excludes non-geostrophic current components.",
        "point": true,
        "static": false,
        "imagery": "Ocean currents",
        "legend": "/api/maps/ocean/CURRENTS/legend.png",
        "legendTitle": "Ocean currents · m/s",
        "monthly": false,
        "coverage": "2017-02-13/2026-09-28/P1D",
        "dataProvider": "NOAA CoastWatch",
        "dataUrl": "https://coastwatch.pfeg.noaa.gov/erddap/",
        "sourceUrl": "https://coastwatch.pfeg.noaa.gov/erddap/",
        "image": "/api/maps/ocean/CURRENTS/{date}.png",
        "dataStart": "2017-02-13",
        "dataEnd": "2026-09-28",
        "dataResolution": "daily",
        "coverageNote": "NOAA CoastWatch numerical product. Land and excluded coastal or polar pixels remain masked; unavailable pixels are not zero."
      },
      {
        "id": "SST_ANOMALY",
        "name": "Sea surface temperature anomaly",
        "unit": "°C",
        "layer": "GHRSST_L4_MUR_Sea_Surface_Temperature_Anomalies",
        "provider": "NASA GHRSST / MUR",
        "description": "NOAA MUR temperature anomaly relative to its 2003–2014 day-of-year climatology. The NASA imagery uses its own reference climatology; map and point anomalies are separate products.",
        "point": true,
        "static": false,
        "imagery": "Sea surface temperature anomaly",
        "legend": "https://gibs.earthdata.nasa.gov/legends/GHRSST_Sea_Surface_Temperature_Anomalies_H.png",
        "legendTitle": "Sea surface temperature anomaly · see provider units",
        "monthly": false,
        "coverage": "2019-07-23/2021-02-19/P1D,2021-02-22/2022-11-08/P1D,2022-11-10/2023-02-01/P1D,2023-02-04/2023-04-21/P1D,2023-04-23/2024-07-01/P1D,2024-07-03/2026-01-09/P1D,2026-01-11/2026-11-13/P1D",
        "sourceUrl": "https://gibs.earthdata.nasa.gov/wms/epsg3857/best/?request=GetMetadata&layer=GHRSST_L4_MUR_Sea_Surface_Temperature_Anomalies",
        "coverageNote": "Sea surface temperature departure from the product’s climatology. Positive values indicate warmer water than its reference, not greater wave height.",
        "dataProvider": "NASA JPL MUR · NOAA ERDDAP",
        "dataStart": "2001-01-01",
        "dataResolution": "daily"
      },
      {
        "id": "EVAPORATION",
        "name": "Land evaporation",
        "unit": "mm/day",
        "layer": "MERRA2_Evaporation_from_Turbulence_Monthly",
        "provider": "MERRA-2",
        "description": "Daily modeled evaporation over land from NASA POWER EVLAND. The map uses monthly MERRA-2 evaporation. Ocean evaporation is outside the point-series scope.",
        "point": true,
        "static": false,
        "imagery": "Evaporation",
        "legend": "https://gibs.earthdata.nasa.gov/legends/MERRA2_Evaporation_from_Turbulence_Monthly_H.png",
        "legendTitle": "Evaporation",
        "monthly": true,
        "coverage": "1980-01-01/2026-08-01/P1M",
        "dataProvider": "NASA POWER",
        "dataStart": "2015-03-31",
        "dataResolution": "daily"
      },
      {
        "id": "GROUNDWATER",
        "name": "Groundwater storage anomaly",
        "unit": "mm water equivalent",
        "layer": "G3P_gwsa",
        "provider": "GFZ / GravIS G3P v1.12",
        "description": "Monthly groundwater storage anomaly from the GFZ G3P prototype: GRACE total storage minus modeled soil, glacier, snow and surface-water components. It is not an absolute aquifer volume. Numerical history is the provider’s mean for the containing aquifer/basin/climate region, not a point measurement. Record ends September 2023.",
        "point": true,
        "static": false,
        "imagery": "Groundwater storage anomaly",
        "legend": "https://gravis.gfz.de/legendy/G3P/gwsa/50",
        "legendTitle": "Groundwater storage anomaly · mm water equivalent",
        "monthly": true,
        "coverage": "",
        "image": "/api/maps/gravis/gwsa/{date}.png",
        "gravisField": "gwsa",
        "sourceUrl": "https://gravis.gfz.de/gws",
        "availableDates": [
          "2002-04-16",
          "2002-05-16",
          "2002-08-16",
          "2002-09-16",
          "2002-10-16",
          "2002-11-16",
          "2002-12-16",
          "2003-01-16",
          "2003-02-16",
          "2003-03-16",
          "2003-04-16",
          "2003-05-16",
          "2003-07-16",
          "2003-08-16",
          "2003-09-16",
          "2003-10-16",
          "2003-11-16",
          "2003-12-16",
          "2004-01-16",
          "2004-02-16",
          "2004-03-16",
          "2004-04-16",
          "2004-05-16",
          "2004-06-16",
          "2004-07-16",
          "2004-08-16",
          "2004-09-16",
          "2004-10-16",
          "2004-11-16",
          "2004-12-16",
          "2005-01-16",
          "2005-02-16",
          "2005-03-16",
          "2005-04-16",
          "2005-05-16",
          "2005-07-16",
          "2005-08-16",
          "2005-09-16",
          "2005-10-16",
          "2005-11-16",
          "2005-12-16",
          "2006-01-16",
          "2006-02-16",
          "2006-03-16",
          "2006-04-16",
          "2006-05-16",
          "2006-06-16",
          "2006-07-16",
          "2006-08-16",
          "2006-09-16",
          "2006-10-16",
          "2006-11-16",
          "2006-12-16",
          "2007-01-16",
          "2007-02-16",
          "2007-03-16",
          "2007-04-16",
          "2007-05-16",
          "2007-06-16",
          "2007-07-16",
          "2007-08-16",
          "2007-09-16",
          "2007-10-16",
          "2007-11-16",
          "2007-12-16",
          "2008-01-16",
          "2008-02-16",
          "2008-03-16",
          "2008-04-16",
          "2008-05-16",
          "2008-06-16",
          "2008-07-16",
          "2008-08-16",
          "2008-09-16",
          "2008-10-16",
          "2008-11-16",
          "2008-12-16",
          "2009-01-16",
          "2009-02-16",
          "2009-03-16",
          "2009-04-16",
          "2009-05-16",
          "2009-06-16",
          "2009-07-16",
          "2009-08-16",
          "2009-09-16",
          "2009-10-16",
          "2009-11-16",
          "2009-12-16",
          "2010-01-16",
          "2010-02-16",
          "2010-03-16",
          "2010-04-16",
          "2010-05-16",
          "2010-06-16",
          "2010-07-16",
          "2010-08-16",
          "2010-09-16",
          "2010-10-16",
          "2010-11-16",
          "2010-12-16",
          "2011-02-16",
          "2011-03-16",
          "2011-04-16",
          "2011-05-16",
          "2011-07-16",
          "2011-08-16",
          "2011-09-16",
          "2011-10-16",
          "2011-11-16",
          "2011-12-16",
          "2012-01-16",
          "2012-02-16",
          "2012-03-16",
          "2012-04-16",
          "2012-06-16",
          "2012-07-16",
          "2012-08-16",
          "2012-09-16",
          "2012-11-16",
          "2012-12-16",
          "2013-01-16",
          "2013-02-16",
          "2013-04-16",
          "2013-05-16",
          "2013-06-16",
          "2013-07-16",
          "2013-10-16",
          "2013-11-16",
          "2013-12-16",
          "2014-01-16",
          "2014-03-16",
          "2014-04-16",
          "2014-05-16",
          "2014-06-16",
          "2014-08-16",
          "2014-09-16",
          "2014-10-16",
          "2014-11-16",
          "2015-01-16",
          "2015-02-16",
          "2015-03-16",
          "2015-04-16",
          "2015-05-16",
          "2015-07-16",
          "2015-08-16",
          "2015-09-16",
          "2015-12-16",
          "2016-01-16",
          "2016-02-16",
          "2016-03-16",
          "2016-05-16",
          "2016-06-16",
          "2016-07-16",
          "2016-08-16",
          "2016-11-16",
          "2016-12-16",
          "2017-01-16",
          "2017-03-16",
          "2017-04-16",
          "2017-05-16",
          "2017-06-16",
          "2018-06-16",
          "2018-07-16",
          "2018-10-16",
          "2018-11-16",
          "2018-12-16",
          "2019-01-16",
          "2019-02-16",
          "2019-03-16",
          "2019-04-16",
          "2019-05-16",
          "2019-06-16",
          "2019-07-16",
          "2019-08-16",
          "2019-09-16",
          "2019-10-16",
          "2019-11-16",
          "2019-12-16",
          "2020-01-16",
          "2020-02-16",
          "2020-03-16",
          "2020-04-16",
          "2020-05-16",
          "2020-06-16",
          "2020-07-16",
          "2020-08-16",
          "2020-09-16",
          "2020-10-16",
          "2020-11-16",
          "2020-12-16",
          "2021-01-16",
          "2021-02-16",
          "2021-03-16",
          "2021-04-16",
          "2021-05-16",
          "2021-06-16",
          "2021-07-16",
          "2021-08-16",
          "2021-09-16",
          "2021-10-16",
          "2021-11-16",
          "2021-12-16",
          "2022-01-16",
          "2022-02-16",
          "2022-03-16",
          "2022-04-16",
          "2022-05-16",
          "2022-06-16",
          "2022-07-16",
          "2022-08-16",
          "2022-09-16",
          "2022-10-16",
          "2022-11-16",
          "2022-12-16",
          "2023-01-16",
          "2023-02-16",
          "2023-03-16",
          "2023-04-16",
          "2023-05-16",
          "2023-06-16",
          "2023-07-16",
          "2023-08-16",
          "2023-09-16"
        ],
        "coverageNote": "GFZ G3P prototype monthly anomalies, baseline April 2002–December 2020; 250 km smoothing. Monthly groundwater storage anomaly from the GFZ G3P prototype: GRACE total storage minus modeled soil, glacier, snow and surface-water components. It is not an absolute aquifer volume.",
        "legendStops": [
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(102,0,31)"
          },
          {
            "label": "",
            "color": "rgb(103,0,31)"
          },
          {
            "label": "",
            "color": "rgb(116,4,33)"
          },
          {
            "label": "",
            "color": "rgb(130,8,35)"
          },
          {
            "label": "",
            "color": "rgb(143,13,37)"
          },
          {
            "label": "",
            "color": "rgb(157,17,39)"
          },
          {
            "label": "",
            "color": "rgb(170,21,41)"
          },
          {
            "label": "",
            "color": "rgb(181,30,46)"
          },
          {
            "label": "",
            "color": "rgb(188,44,52)"
          },
          {
            "label": "",
            "color": "rgb(194,57,58)"
          },
          {
            "label": "",
            "color": "rgb(201,71,65)"
          },
          {
            "label": "",
            "color": "rgb(208,84,71)"
          },
          {
            "label": "",
            "color": "rgb(214,98,78)"
          },
          {
            "label": "",
            "color": "rgb(220,111,88)"
          },
          {
            "label": "",
            "color": "rgb(226,124,98)"
          },
          {
            "label": "",
            "color": "rgb(231,137,108)"
          },
          {
            "label": "",
            "color": "rgb(237,150,118)"
          },
          {
            "label": "",
            "color": "rgb(243,163,128)"
          },
          {
            "label": "",
            "color": "rgb(245,173,140)"
          },
          {
            "label": "",
            "color": "rgb(247,183,153)"
          },
          {
            "label": "",
            "color": "rgb(248,192,165)"
          },
          {
            "label": "",
            "color": "rgb(250,202,178)"
          },
          {
            "label": "",
            "color": "rgb(251,212,190)"
          },
          {
            "label": "",
            "color": "rgb(252,220,201)"
          },
          {
            "label": "",
            "color": "rgb(251,225,210)"
          },
          {
            "label": "",
            "color": "rgb(250,230,219)"
          },
          {
            "label": "",
            "color": "rgb(249,235,227)"
          },
          {
            "label": "",
            "color": "rgb(248,240,236)"
          },
          {
            "label": "",
            "color": "rgb(247,245,245)"
          },
          {
            "label": "",
            "color": "rgb(241,244,245)"
          },
          {
            "label": "",
            "color": "rgb(234,240,244)"
          },
          {
            "label": "",
            "color": "rgb(227,237,243)"
          },
          {
            "label": "",
            "color": "rgb(219,234,242)"
          },
          {
            "label": "",
            "color": "rgb(212,230,240)"
          },
          {
            "label": "",
            "color": "rgb(203,226,238)"
          },
          {
            "label": "",
            "color": "rgb(191,220,235)"
          },
          {
            "label": "",
            "color": "rgb(179,214,231)"
          },
          {
            "label": "",
            "color": "rgb(167,208,228)"
          },
          {
            "label": "",
            "color": "rgb(156,202,224)"
          },
          {
            "label": "",
            "color": "rgb(143,195,221)"
          },
          {
            "label": "",
            "color": "rgb(129,186,216)"
          },
          {
            "label": "",
            "color": "rgb(115,177,211)"
          },
          {
            "label": "",
            "color": "rgb(100,168,206)"
          },
          {
            "label": "",
            "color": "rgb(86,159,201)"
          },
          {
            "label": "",
            "color": "rgb(72,150,196)"
          },
          {
            "label": "",
            "color": "rgb(63,141,192)"
          },
          {
            "label": "",
            "color": "rgb(57,133,188)"
          },
          {
            "label": "",
            "color": "rgb(50,125,184)"
          },
          {
            "label": "",
            "color": "rgb(44,117,179)"
          },
          {
            "label": "",
            "color": "rgb(38,109,175)"
          },
          {
            "label": "",
            "color": "rgb(32,101,170)"
          },
          {
            "label": "",
            "color": "rgb(27,90,156)"
          },
          {
            "label": "",
            "color": "rgb(21,80,142)"
          },
          {
            "label": "",
            "color": "rgb(16,70,128)"
          },
          {
            "label": "",
            "color": "rgb(11,60,114)"
          },
          {
            "label": "",
            "color": "rgb(6,50,100)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          },
          {
            "label": "",
            "color": "rgb(5,48,96)"
          }
        ],
        "legendTicks": [
          {
            "label": "-800",
            "position": 0
          },
          {
            "label": "0",
            "position": 0.42105263157894735
          },
          {
            "label": "1000",
            "position": 0.9473684210526316
          }
        ],
        "legendContinuous": true,
        "legendUnit": "Water-equivalent anomaly · mm",
        "dataProvider": "GFZ G3P · regional mean",
        "dataUrl": "https://gravis.gfz.de/gws",
        "dataStart": "2002-04-01",
        "dataEnd": "2023-09-30",
        "dataResolution": "monthly"
      }
    ]
  }
};
export function getVariable(system, id) { return systems[system].variables.find(v => v.id === id) || systems[system].variables[0]; }
