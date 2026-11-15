# Geographic reference data

Bundled public-domain Natural Earth 1:10m data, downloaded from the project's official source repository on 2026-11-14:

- `cities.json.gz`: 7,342 named cities/towns; derived from `ne_10m_populated_places_simple.geojson`.
- `water-bodies.json.gz`: named marine areas and lakes; derived from `ne_10m_geography_marine_polys.geojson` and `ne_10m_lakes.geojson`.

Original source: https://github.com/nvkelso/natural-earth-vector/tree/master/geojson
Terms: https://www.naturalearthdata.com/about/terms-of-use/ (public domain).

Only names, administrative labels and original geometries are retained. These files support approximate contextual labels, not legal boundaries or navigation. Marine polygons are generalized physical label regions; coastlines are approximate. City coverage is a curated gazetteer, not every settlement in the world. A nearest-city label identifies the nearest indexed city and its great-circle distance, rather than claiming that the point lies inside that city's administrative limits. Coordinate requests stay on the local server; no third-party geocoder is contacted.
