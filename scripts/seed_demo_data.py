from pathlib import Path
import json

root = Path(__file__).resolve().parent.parent / "arc_service" / "app" / "data"
(root / "entitlements.mock.json").write_text(json.dumps({
  "demo_account": {
    "accountId": "demo_account",
    "ownsEveryVST": True,
    "ownedProducts": [],
    "ownedBundles": ["complete_collection"],
    "extraSeatQuantity": 2,
    "billingState": "active"
  }
}, indent=2))
print("Seeded demo ARC data")
