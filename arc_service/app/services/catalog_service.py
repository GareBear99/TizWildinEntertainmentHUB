from pathlib import Path
import json

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "products.catalog.json"

def load_catalog():
    return json.loads(DATA_PATH.read_text())
