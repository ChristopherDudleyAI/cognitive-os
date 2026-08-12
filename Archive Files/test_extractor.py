import py_compile
import json
from ingestion.extractor import Extractor

# Test syntax
try:
    py_compile.compile('ingestion/extractor.py')
    print("Extractor syntax OK")
except Exception as e:
    print(f"Syntax error: {e}")

# Test extraction
try:
    config = json.load(open('config.json'))
    e = Extractor(
        config['claude']['api_key'],
        config['claude']['model']
    )
    result = e.extract(
        "Proverbs 1:7 The fear of the LORD "
        "is the beginning of knowledge. "
        "Proverbs 3:5 Trust in the LORD "
        "with all thine heart."
    )
    print(f"Extracted {len(result)} memories")
    for r in result:
        print(f"- {r.get('memory_text','')[:60]}")
except Exception as e:
    print(f"Extraction error: {e}")