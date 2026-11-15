# Shoreline reference

`coastlines.geojson` retains only the line geometry from Natural Earth 1:10m `ne_10m_coastline.geojson`. `lake-shores.geojson` retains rings from the named Natural Earth 1:10m lakes bundled in backend/data. Neither file includes administrative country borders. These are generalized cartographic shorelines, not surveyed tidal or legal boundaries.

Source: https://github.com/nvkelso/natural-earth-vector/tree/master/geojson
License: public domain, https://www.naturalearthdata.com/about/terms-of-use/

The app serves these files locally and compresses large responses with gzip. Source geometries are not simplified further during preparation; MapLibre handles display-level simplification.
