"""GFZ GravIS G3P map imagery, retaining the provider's colors and monthly dates.

The public viewer publishes three repeated EPSG:4326 worlds in each PNG. Crop
its central world and resample to Web Mercator before placing it in MapLibre.
This adapter serves visualization only, never inferred numerical observations.
"""
import io
import json
import math
import time
from datetime import date, timedelta
from functools import lru_cache
from urllib.request import urlopen
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image

FIELDS = {'gwsa', 'glac'}
BASE = 'https://gravis.gfz.de'

def read_url(url):
    with urlopen(url, timeout=20) as response:
        content = response.read(8_000_001)
    if len(content) > 8_000_000:
        raise ValueError('Provider response exceeds image limit')
    return content

def parse_legend(svg):
    root = ET.fromstring(svg)
    ns = {'s': 'http://www.w3.org/2000/svg'}
    rects = root.findall('s:rect', ns)
    top = min(float(r.attrib['y']) for r in rects)
    bottom = max(float(r.attrib['y'])+float(r.attrib['height']) for r in rects)
    stops = []
    for rect in sorted(rects, key=lambda r: float(r.attrib['y']), reverse=True):
        color = rect.attrib['fill'].replace('rgba(', '').rstrip(')').split(',')[:3]
        stops.append({'label': '', 'color': 'rgb('+','.join(color)+')'})
    labels = []
    for text in root.findall('s:text', ns):
        try:
            float(text.text)
        except (ValueError, TypeError):
            continue
        # Provider text is drawn five pixels below its corresponding tick.
        offset = 1-(float(text.attrib['y'])-5-top)/(bottom-top)
        labels.append({'label': text.text, 'position': max(0, min(1, offset))})
    labels.sort(key=lambda item: item['position'])
    if len(labels) > 5:
        labels = [labels[0], min(labels, key=lambda t: abs(float(t['label']))), labels[-1]]
    return {'legendStops': stops, 'legendTicks': labels,
            'legendContinuous': True, 'legendUnit': 'Water-equivalent anomaly · mm'}

@lru_cache(maxsize=16)
def _metadata(field, hour):
    if field not in FIELDS:
        raise ValueError('Unknown G3P field')
    payload = json.loads(read_url(f'{BASE}/chartdata/G3P/{field}/aquifers/'))
    times = {}
    for row in payload['data'][0]:
        value = row.get('v')
        if not isinstance(value, (float, int)) or not math.isfinite(value):
            continue
        observed = date(int(row['y']), 1, 1)+timedelta(days=int(row['d'])-1)
        # GFZ identifies this month as faulty for groundwater/SWE products.
        if field == 'gwsa' and observed.strftime('%Y-%m') == '2005-06':
            continue
        times[observed.isoformat()] = f"{row['y']}_{row['d']}"
    legend = parse_legend(read_url(f'{BASE}/legendy/G3P/{field}/50'))
    return {'availableDates': sorted(times), 'providerTimes': times, **legend,
            'sourceUrl': f'{BASE}/gws', 'provider': 'GFZ / GravIS G3P v1.12'}

def metadata(field):
    return _metadata(field, int(time.time()//3600))

def reproject_image(content, size=1024, world_copies=3):
    source = Image.open(io.BytesIO(content)).convert('RGBA')
    if source.width % world_copies or source.width < world_copies:
        raise ValueError('Unexpected provider image extent')
    width = source.width//world_copies
    middle=world_copies//2
    source = source.crop((width*middle, 0, width*(middle+1), source.height))
    source = source.resize((size, source.height), Image.Resampling.BILINEAR)
    pixels = np.asarray(source, dtype=np.float32)
    # Mercator ordinate -> latitude -> source equirectangular pixel center.
    mercator_y = math.pi*(1-2*(np.arange(size)+.5)/size)
    latitude = np.degrees(np.arctan(np.sinh(mercator_y)))
    rows = np.clip((90-latitude)/180*source.height-.5, 0, source.height-1)
    lower = np.floor(rows).astype(int)
    upper = np.minimum(lower+1, source.height-1)
    weights = (rows-lower)[:, None, None]
    pixels[:, :, :3] *= pixels[:, :, 3:4]/255
    output = pixels[lower]*(1-weights)+pixels[upper]*weights
    alpha = output[:, :, 3:4]/255
    output[:, :, :3] = np.divide(output[:, :, :3], alpha, out=np.zeros_like(output[:, :, :3]), where=alpha>0)
    image = Image.fromarray(np.clip(np.round(output), 0, 255).astype('uint8'))
    stream = io.BytesIO()
    image.save(stream, format='PNG')
    return stream.getvalue()

@lru_cache(maxsize=48)
def image(field, observed):
    info = metadata(field)
    provider_time = info['providerTimes'].get(observed)
    if not provider_time:
        raise ValueError('No provider image for this observation date')
    return reproject_image(read_url(f'{BASE}/model/G3P/G3P/{field}/50/{provider_time}'))
