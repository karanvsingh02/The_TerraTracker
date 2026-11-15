from datetime import date, timedelta
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.adapters.power import normalize
from backend.services.trends import analyze, aggregate, mann_kendall

def daily_series():
    start=date(2001,1,1)
    return [{'date':(start+timedelta(days=i)).isoformat(),'value':10 + (start+timedelta(days=i)).year-2001} for i in range((date(2011,1,1)-start).days)]

def test_known_slope():
    result=analyze(daily_series(),'T2M','C')
    assert result['slopePerDecade'] == pytest.approx(10,abs=.01)
    assert result['pValue'] < .001
    assert result['sampleSize'] == 10

def test_constant_and_missing():
    rows=daily_series()
    for row in rows: row['value']=4
    result=analyze(rows,'T2M','C')
    assert result['pValue']==1
    assert result['slopePerDecade']==0
    assert result['mannKendall']['pValue']==1
    for row in rows[:365]: row['value']=None
    assert len(aggregate(rows,'annual')) == 9

def test_partial_year_excluded():
    assert aggregate([{'date':'2024-01-01','value':3}],'annual') == []

def test_fill_values():
    payload={'properties':{'parameter':{'T2M':{'20240101':-999,'20240102':12}}},'parameters':{'T2M':{'units':'C'}},'header':{'fill_value':-999}}
    result=normalize(payload,'T2M',0,0,'https://example.test')
    assert result['data'][0]['value'] is None
    assert result['observationTime']=='2024-01-02'

def test_precipitation_sum():
    rows=[{'date':f'2024-01-{day:02}','value':2} for day in range(1,32)]
    assert aggregate(rows,'monthly',True)[0]['value']==62

def test_circular_and_seasonal_guards():
    with pytest.raises(ValueError): analyze(daily_series(),'WD10M','degrees')
    with pytest.raises(ValueError): analyze(daily_series(),'T2M','C',deseasonalize=True)

def test_mann_kendall():
    assert mann_kendall(list(range(20)))['pValue'] < .001
    assert mann_kendall([1,2,1,2,1,2])['pValue'] > .05

def test_routes_and_validation():
    client=TestClient(app)
    for route in ['/dashboard','/atmosphere','/oceans','/land','/climate','/cryosphere','/compare','/about']:
        assert client.get(route).status_code==200
    assert client.get('/api/observations/point?lat=91&lon=0').status_code==422
    assert client.get('/api/observations/point?lat=0&lon=0&start=2024-02-30').status_code==422
    assert client.get('/api/observations/point?lat=0&lon=0&variable=FAKE').status_code==400
    assert client.get('/api/unknown').status_code==404

def test_api_pipeline(monkeypatch):
    monkeypatch.setattr('backend.main.fetch_point',lambda *args: {'data':daily_series(),'unit':'C'})
    response=TestClient(app).get('/api/observations/point?lat=0&lon=0')
    assert response.status_code==200
    assert response.json()['analysis']['sampleSize']==10

def test_local_preview_cors():
    client = TestClient(app)
    for origin in ['http://127.0.0.1:5500', 'http://localhost:5501', 'http://localhost:63342']:
        response = client.get('/api/health', headers={'Origin': origin})
        assert response.headers['access-control-allow-origin'] == origin
    response = client.get('/api/health', headers={'Origin': 'https://unrelated.example'})
    assert 'access-control-allow-origin' not in response.headers

def test_new_atmosphere_parameters(monkeypatch):
    called = []
    def fake_point(lat, lon, variable, start, end):
        called.append(variable)
        return {'data': daily_series(), 'unit': 'native'}
    monkeypatch.setattr('backend.main.fetch_point', fake_point)
    client = TestClient(app)
    for variable in ['TQV', 'ALLSKY_SFC_SW_DWN']:
        assert client.get('/api/observations/point', params={'lat': 0, 'lon': 0, 'variable': variable}).status_code == 200
    assert called == ['TQV', 'ALLSKY_SFC_SW_DWN']

def test_place_names_and_city_fallback():
    from backend.services.places import resolve_place
    assert resolve_place(26.76, -17.56)['label'] == 'Atlantic Ocean'
    assert resolve_place(54, 3)['label'] == 'North Sea'
    result = resolve_place(29.7604, -95.3698)
    assert result['kind'] == 'nearest_city'
    assert result['nearestCity']['name'] == 'Houston'
    assert 'Near Houston' in result['label']
    assert result['nearestCity']['distanceKm'] < 5
    assert resolve_place(-1, 33)['kind'] == 'lake'

def test_place_polygons_respect_holes():
    from backend.services.places import inside_polygon
    outer = [[0,0],[10,0],[10,10],[0,10],[0,0]]
    hole = [[4,4],[6,4],[6,6],[4,6],[4,4]]
    assert inside_polygon(2,2,[outer,hole])
    assert not inside_polygon(5,5,[outer,hole])
    assert not inside_polygon(20,20,[outer])

def test_place_endpoint():
    client = TestClient(app)
    response = client.get('/api/places/reverse?lat=26.76&lon=-17.56')
    assert response.status_code == 200
    assert response.json()['label'] == 'Atlantic Ocean'
    assert client.get('/api/places/reverse?lat=91&lon=0').status_code == 422

def test_gravis_reprojection_crops_middle_world():
    import io
    import numpy as np
    from PIL import Image
    from backend.adapters.gravis import reproject_image
    source = np.zeros((12, 36, 4), dtype='uint8')
    source[:, :12] = [255,0,0,255]
    source[:, 12:24] = [0,255,0,255]
    source[:, 24:] = [0,0,255,255]
    stream=io.BytesIO()
    Image.fromarray(source).save(stream,format='PNG')
    result=Image.open(io.BytesIO(reproject_image(stream.getvalue(),size=24)))
    assert result.size == (24,24)
    assert result.getpixel((12,12)) == (0,255,0,255)

def test_gravis_legend_preserves_provider_tick_positions():
    from backend.adapters.gravis import parse_legend
    svg=b'<svg xmlns="http://www.w3.org/2000/svg"><rect y="0" height="50" fill="rgba(0,0,255,255)"/><rect y="50" height="50" fill="rgba(255,0,0,255)"/><text y="105">-10</text><text y="55">0</text><text y="5">10</text></svg>'
    result=parse_legend(svg)
    assert result['legendStops'][0]['color'] == 'rgb(255,0,0)'
    assert result['legendTicks'] == [{'label':'-10','position':0},{'label':'0','position':.5},{'label':'10','position':1}]

def test_gravis_api_uses_json_errors_and_png(monkeypatch):
    monkeypatch.setattr('backend.main.gravis.metadata',lambda field: {'availableDates':['2023-09-16'],'providerTimes':{'2023-09-16':'2023_259'}})
    monkeypatch.setattr('backend.main.gravis.image',lambda field,observed: b'PNG fixture')
    client=TestClient(app)
    response=client.get('/api/maps/gravis/gwsa/metadata')
    assert response.json()=={'availableDates':['2023-09-16']}
    response=client.get('/api/maps/gravis/gwsa/2023-09-16.png')
    assert response.headers['content-type']=='image/png'
    assert client.get('/api/maps/gravis/not-a-field/metadata').status_code==422
