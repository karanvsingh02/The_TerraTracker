"""Offline geographic labels from public-domain Natural Earth reference data."""
import gzip
import json
from functools import lru_cache
from pathlib import Path
import numpy as np

DATA = Path(__file__).resolve().parent.parent / 'data'

def inside_ring(x, y, ring):
    inside = False
    previous = ring[-1]
    for current in ring:
        x1, y1 = previous[:2]
        x2, y2 = current[:2]
        if (y1 > y) != (y2 > y) and x < (x2-x1)*(y-y1)/(y2-y1)+x1:
            inside = not inside
        previous = current
    return inside

def inside_polygon(lon, lat, rings):
    return inside_ring(lon, lat, rings[0]) and not any(inside_ring(lon, lat, hole) for hole in rings[1:])

@lru_cache(maxsize=1)
def reference_data():
    with gzip.open(DATA / 'cities.json.gz', 'rt', encoding='utf-8') as file:
        cities = json.load(file)
    city_coords = np.radians(np.array([city['coordinates'][:2] for city in cities]))
    with gzip.open(DATA / 'water-bodies.json.gz', 'rt', encoding='utf-8') as file:
        bodies = json.load(file)
    polygons = []
    for body in bodies:
        geometry = body['geometry']
        parts = [geometry['coordinates']] if geometry['type'] == 'Polygon' else geometry['coordinates']
        for rings in parts:
            if not rings or not rings[0]:
                continue
            x, y = zip(*[coordinate[:2] for coordinate in rings[0]])
            bbox = min(x), min(y), max(x), max(y)
            area = (bbox[2]-bbox[0]) * (bbox[3]-bbox[1])
            polygons.append((area, bbox, body, rings))
    # Small named bays/lakes take precedence over broader overlapping seas/oceans.
    polygons.sort(key=lambda item: item[0])
    return cities, city_coords, polygons

@lru_cache(maxsize=2048)
def resolve_place(latitude, longitude):
    cities, coords, polygons = reference_data()
    lon, lat = np.radians([longitude, latitude])
    delta_lat = coords[:, 1] - lat
    delta_lon = coords[:, 0] - lon
    haversine = np.sin(delta_lat/2)**2 + np.cos(lat)*np.cos(coords[:, 1])*np.sin(delta_lon/2)**2
    distances = 6371.0088 * 2 * np.arcsin(np.sqrt(np.clip(haversine, 0, 1)))
    index = int(np.argmin(distances))
    city = cities[index]
    parts = list(dict.fromkeys(part for part in [city['name'], city.get('region'), city.get('country')] if part))
    nearest = {'name': city['name'], 'region': city.get('region'), 'country': city.get('country'),
               'label': ', '.join(parts), 'distanceKm': round(float(distances[index]), 1)}
    water = None
    for _, bbox, body, rings in polygons:
        if bbox[0] <= longitude <= bbox[2] and bbox[1] <= latitude <= bbox[3] and inside_polygon(longitude, latitude, rings):
            water = body
            break
    label = water['name'] if water else f"Near {nearest['label']} · {nearest['distanceKm']:g} km away"
    return {'label': label, 'kind': water['kind'] if water else 'nearest_city',
            'nearestCity': nearest, 'source': 'Natural Earth',
            'sourceUrl': 'https://www.naturalearthdata.com/',
            'note': 'Approximate geographic reference. Nearest city means nearest city in the bundled gazetteer; smaller settlements may be closer.'}
