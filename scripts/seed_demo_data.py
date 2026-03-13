from pathlib import Path
import json
root = Path(__file__).resolve().parent.parent / 'arc_service' / 'app' / 'data'
(root / 'entitlements.mock.json').write_text(json.dumps({'demo_account': {'accountId': 'demo_account', 'ownsEveryVST': True, 'ownedProducts': [], 'ownedBundles': ['complete_collection'], 'extraSeatQuantity': 2, 'billingState': 'active'}, 'free_account': {'accountId': 'free_account', 'ownsEveryVST': False, 'ownedProducts': [], 'ownedBundles': [], 'extraSeatQuantity': 0, 'billingState': 'active'}}, indent=2))
(root / 'seats.mock.json').write_text(json.dumps({}, indent=2))
(root / 'install_scans.mock.json').write_text(json.dumps([], indent=2))
(root / 'install_receipts.mock.json').write_text(json.dumps([], indent=2))
(root / 'auth_tokens.mock.json').write_text(json.dumps({}, indent=2))
(root / 'webhooks.mock.json').write_text(json.dumps([], indent=2))
print('Seeded demo ARC data')
