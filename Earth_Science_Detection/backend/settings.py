"""Server-only settings; read local credentials without returning or logging them."""
import os
from pathlib import Path
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parent.parent

def earthdata_credentials():
    # Read on each access so creating/updating .env does not require a restart.
    path = ROOT / '.env' if (ROOT / '.env').is_file() else ROOT / 'earthdata.env'
    values = dotenv_values(path, interpolate=False) if path.is_file() else {}
    username = os.environ.get('EARTHDATA_USERNAME') or values.get('EARTHDATA_USERNAME')
    password = os.environ.get('EARTHDATA_PASSWORD') or values.get('EARTHDATA_PASSWORD')
    return username, password

def earthdata_configured():
    username, password = earthdata_credentials()
    return bool(username and password)
