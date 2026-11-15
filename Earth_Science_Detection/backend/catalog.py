VARIABLES = {
    'EVAPORATION': {'name': 'Land evaporation', 'unit': 'mm/day', 'description': 'POWER evaporation over land.'},
    'SNOW': {'name': 'Snow cover', 'unit': '% land area', 'description': 'POWER modeled land snow-cover fraction, converted to percent.'},
    'ALBEDO': {'name': 'Surface albedo', 'unit': 'dimensionless', 'description': 'POWER all-sky surface albedo; map uses MERRA-2.'},
    'SOIL_TEMPERATURE': {'name': 'Soil temperature', 'unit': '°C', 'description': 'POWER modeled upper-layer soil temperature; map uses SMAP.'},
    'T2M': {'name': 'Air temperature', 'unit': '°C', 'description': 'Temperature of the air at 2 meters above the surface.'},
    'RH2M': {'name': 'Relative humidity', 'unit': '%', 'description': 'Water vapor relative to saturation at 2 meters.'},
    'PS': {'name': 'Atmospheric pressure', 'unit': 'kPa', 'description': 'Atmospheric pressure at the surface; native POWER units.'},
    'WS10M': {'name': 'Wind speed', 'unit': 'm/s', 'description': 'Wind speed at 10 meters above the surface.'},
    'WD10M': {'name': 'Wind direction', 'unit': 'degrees', 'description': 'Circular wind direction. Linear trend analysis is not appropriate.'},
    'PRECTOTCORR': {'name': 'Precipitation', 'unit': 'mm/day', 'description': 'Bias-corrected precipitation rate; totals use daily accumulation.'},
    'TQV': {'name': 'Water vapor', 'unit': 'kg/m²', 'description': 'Total column precipitable water.'},
    'ALLSKY_SFC_SW_DWN': {'name': 'Solar radiation', 'unit': 'MJ/m²/day', 'description': 'All-sky surface shortwave downward solar energy.'},
}
