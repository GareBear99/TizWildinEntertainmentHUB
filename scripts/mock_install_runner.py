from __future__ import annotations
import argparse
import json
from pathlib import Path
import urllib.request

def post_json(url: str, body: dict) -> dict:
    req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode('utf-8'))

def main():
    parser = argparse.ArgumentParser(description='Mock install runner for the HUB ARC service')
    parser.add_argument('--arc', default='http://127.0.0.1:8000')
    parser.add_argument('--account', default='demo_account')
    parser.add_argument('--machine', default='hub_desktop')
    parser.add_argument('--products', nargs='*', default=['freeeq8', 'therum', 'paintmask'])
    parser.add_argument('--out', default='install_receipts_local.json')
    args = parser.parse_args()

    plan = post_json(args.arc + '/download-plan', {'accountId': args.account, 'machineId': args.machine, 'requestedProducts': args.products})
    receipts = post_json(args.arc + '/record-receipt', {'accountId': args.account, 'machineId': args.machine, 'requestedProducts': args.products})
    Path(args.out).write_text(json.dumps({'plan': plan, 'receipts': receipts}, indent=2))
    print(f"wrote {args.out} with {len(receipts.get('receipts', []))} planned receipts")

if __name__ == '__main__':
    main()
