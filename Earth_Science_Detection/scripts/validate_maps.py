"""Live image audit. Install Pillow, then pass JSON exported from the JS catalog.

Example input: node --input-type=module to export variables + chooseMapDate().
Results distinguish disconnected sources, failed requests and transparent imagery.
"""
import io
import json
import sys
import subprocess
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlencode
from urllib.request import urlopen
from PIL import Image

ENDPOINT = 'https://gibs.earthdata.nasa.gov/wms/epsg3857/best/wms.cgi'

def check(variable):
    row = {'id': variable['id'], 'variable': variable['name'], 'date': variable['date'], 'provider': variable['provider']}
    if not variable.get('layer') and not variable.get('tiles') and not variable.get('image'):
        return {**row, 'status': 'not_connected'}
    if variable.get('image'):
        url = 'http://127.0.0.1:8000' + variable['image'].replace('{date}', variable['date'])
    elif variable.get('tiles'):
        url = variable['tiles'].replace('{z}', '1').replace('{x}', '0').replace('{y}', '0')
    else:
        endpoint = variable.get('endpoint', ENDPOINT)
        # Regional displacement must be checked within its actual study area.
        bbox = '34.4,35.5,39,39' if variable['id'] == 'DISPLACEMENT' else '-180,-85,180,85'
        query = dict(SERVICE='WMS', VERSION='1.1.1', REQUEST='GetMap', LAYERS=variable['layer'],
                     STYLES=variable.get('style', ''), FORMAT='image/png', TRANSPARENT='TRUE', SRS='EPSG:4326',
                     WIDTH=512, HEIGHT=256, BBOX=bbox)
        if variable['date']:
            query['TIME'] = variable['date']
        url = endpoint + ('&' if '?' in endpoint else '?') + urlencode(query)
    try:
        try:
            with urlopen(url, timeout=35) as response:
                data = response.read(6_000_000)
                content_type = response.headers.get('Content-Type')
        except Exception as error:
            # macOS system Python's older TLS can fail against this provider;
            # curl retains certificate verification and negotiates modern TLS.
            if 'TLSV1_ALERT_PROTOCOL_VERSION' not in str(error):
                raise
            data = subprocess.run(['curl','--fail','--silent','--show-error','--max-time','35',url],check=True,capture_output=True).stdout
            content_type = 'image/png' if data.startswith(b'\x89PNG') else 'unknown'
        image = Image.open(io.BytesIO(data)).convert('RGBA')
        alpha = image.getchannel('A')
        nonempty = alpha.getbbox() is not None
        return {**row, 'status': 'image_received' if nonempty else 'transparent_image',
                'contentType': content_type, 'nontransparentPixelFraction': sum(value>0 for value in alpha.getdata())/(image.width*image.height), 'size': image.size, 'requestUrl': url}
    except Exception as error:
        return {**row, 'status': 'request_failed', 'error': str(error), 'requestUrl': url}

if __name__ == '__main__':
    with open(sys.argv[1]) as file:
        variables = json.load(file)
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(check, variables))
    output = json.dumps(results, indent=2)
    if len(sys.argv)>2:
        with open(sys.argv[2], 'w') as file: file.write(output)
    print(json.dumps({'verified':sum(r['status']=='image_received' for r in results), 'issues':[r for r in results if r['status']!='image_received']}, indent=2))
