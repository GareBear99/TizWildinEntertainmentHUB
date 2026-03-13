from pathlib import Path
import requests

BASE = 'http://127.0.0.1:8000'
response = requests.post(f'{BASE}/backups/export', params={'tag': 'manual'})
response.raise_for_status()
body = response.json()
print('Backup written to', body['path'])
