"""NASA POWER point adapter; normalized values and bounded in-memory cache."""
import json
import math
import threading
import time
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import urlopen

_cache = {}
_lock = threading.Lock()

def normalize(payload, variable, latitude, longitude, source_url):
    values = payload.get('properties', {}).get('parameter', {}).get(variable)
    unit = payload.get('parameters', {}).get(variable, {}).get('units')
    if not isinstance(values, dict) or not values or not isinstance(unit, str):
        raise ValueError('NASA returned an unexpected response schema')
    fill = payload.get('header', {}).get('fill_value', -999)
    series = []
    for date, raw in sorted(values.items()):
        parsed = datetime.strptime(date, '%Y%m%d').date().isoformat()
        valid = isinstance(raw, (int, float)) and not isinstance(raw, bool) and math.isfinite(raw) and raw != fill
        series.append({'date': parsed, 'value': raw if valid else None})
    valid_dates = [row['date'] for row in series if row['value'] is not None]
    return dict(source='NASA POWER', sourceUrl=source_url, variable=variable, unit=unit,
                latitude=latitude, longitude=longitude, temporalResolution='daily',
                spatialResolution='Native POWER source grid; point represents a grid cell, not a station',
                observationTime=max(valid_dates) if valid_dates else None, publicationTime=None,
                fetchedAt=datetime.now(timezone.utc).isoformat(), data=series,
                providerHeader=payload.get('header', {}), coordinateReferenceSystem='WGS84',
                spatialAveraging='Single provider grid point', fillValue=fill)

def fetch_point(latitude, longitude, variable, start, end):
    parameter={'ALBEDO':'ALLSKY_SRF_ALB','SOIL_TEMPERATURE':'TSOIL1','SURFACE_MOISTURE':'SFMC','ROOT_MOISTURE':'RZMC','EVAPORATION':'EVLAND','SNOW':'FRSNO'}.get(variable,variable)
    query = urlencode(dict(parameters=parameter, community='AG', latitude=latitude,
                           longitude=longitude, start=start.replace('-', ''), end=end.replace('-', ''),
                           format='JSON', **{'time-standard': 'UTC'}))
    url = 'https://power.larc.nasa.gov/api/temporal/daily/point?' + query
    with _lock:
        cached = _cache.get(url)
        if cached and time.monotonic() - cached[0] < 86400:
            return cached[1]
    with urlopen(url, timeout=45) as response:
        payload = json.loads(response.read(15_000_001))
    result = normalize(payload, parameter, latitude, longitude, url)
    result['variable']=variable
    if variable=='SNOW':
        result['data']=[dict(row,value=row['value']*100 if row['value'] is not None else None) for row in result['data']]
        result['unit']='% land area'
    with _lock:
        if len(_cache) >= 128:
            _cache.pop(next(iter(_cache)))
        _cache[url] = (time.monotonic(), result)
    return result
