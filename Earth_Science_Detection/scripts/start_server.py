"""Start the local tracker independently of the launching Terminal window."""
import fcntl
import json
import os
from pathlib import Path
import socket
import subprocess
import time
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent.parent
URL = 'http://127.0.0.1:8000'
RUNTIME = ROOT / '.runtime'


def healthy():
    try:
        with urlopen(URL + '/api/health', timeout=2) as response:
            status = json.load(response)
        return status.get('status') == 'ok' and 'local-only' in status.get('access', '')
    except (OSError, ValueError):
        return False


def main():
    RUNTIME.mkdir(exist_ok=True)
    with (RUNTIME / 'server-start.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if healthy():
            print('Terra Tracker is already running: ' + URL + '/atmosphere')
            return 0
        python = ROOT / '.venv' / 'bin' / 'python'
        if not python.is_file():
            print('The Python environment is missing. Create .venv and install requirements.txt first.')
            return 1
        with socket.socket() as probe:
            if probe.connect_ex(('127.0.0.1', 8000)) == 0:
                print('Port 8000 is occupied by a different or unresponsive service. No process was stopped.')
                return 1
        logfile = RUNTIME / 'server.log'
        with logfile.open('ab', buffering=0) as log:
            process = subprocess.Popen(
                [str(python), '-m', 'uvicorn', 'backend.main:app', '--host', '127.0.0.1', '--port', '8000'],
                cwd=ROOT, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                start_new_session=True, close_fds=True, env={**os.environ, 'PYTHONUNBUFFERED': '1'})
        (RUNTIME / 'server.pid').write_text(str(process.pid) + '\n')
        for _ in range(40):
            if healthy():
                print('Terra Tracker is ready: ' + URL + '/atmosphere')
                print('The server runs in the background; you can close this Terminal window.')
                return 0
            if process.poll() is not None:
                break
            time.sleep(.5)
        print('Startup did not complete. Details are in ' + str(logfile))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
