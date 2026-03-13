import sys
import requests

BASE = 'http://127.0.0.1:8000'
path = sys.argv[1]
response = requests.post(f'{BASE}/backups/restore', json={'path': path})
response.raise_for_status()
print(response.json())
