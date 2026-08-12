import json
import sys
sys.path.append(".")

from ingestion.extractor import Extractor

with open("config.json", "r") as f:
    config = json.load(f)

extractor = Extractor(
    api_key=config["anthropic_api_key"],
    model=config["model"]
)

test_text = """
DEPOSITION OF JOHN SMITH
Case: Smith v. Jones Construction LLC
Judge: Hon. Patricia Reynolds
Plaintiff's Counsel: Robert Hartley
Defendant's Counsel: Sandra Webb

MR. HARTLEY: Was the deadline met?
WITNESS: No. They finished three months late.
JUDGE REYNOLDS: Overruled. The witness may answer.
MS. WEBB: Objection. Speculation.
"""

print("Running extraction...")
results = extractor.extract(test_text)
print(f"Results type: {type(results)}")
print(f"Results count: {len(results)}")
print(f"First result: {results[0] if results else 'NONE'}")