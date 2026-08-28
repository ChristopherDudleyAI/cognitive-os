"""Repair inverted attorney attribution in already-stored memories.

The guard in `ingestion/structurer.py` catches inversions at ingest time,
but it only protects memories ingested after it existed. Anything stored
earlier keeps whatever the model emitted, and a swapped pair is invisible
-- it produces no error, just an opposing counsel's rulings filed under
our own attorney and vice versa, which quietly corrupts both entities'
pattern evidence.

This applies the same rule to what is already in the database:

    if opposing_counsel is one of the firm's own attorneys
    and source_attorney is NOT one of ours
    then the pair was inverted -- swap it

Anything less clear-cut is reported and left alone. Guessing at an
ambiguous pair would be worse than leaving a visible problem visible.

Run from the project root. Dry run by default:

    python tools/repair_attribution.py
    python tools/repair_attribution.py --apply
"""
import json
import os
import sys

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from storage.memory_db import MemoryDB        # noqa: E402
from storage.vector_db import VectorDB        # noqa: E402

APPLY = '--apply' in sys.argv

try:
    with open('config.json') as fh:
        config = json.load(fh)
except FileNotFoundError:
    sys.exit(
        "config.json not found. Run this from the project root -- "
        "config is loaded by relative path."
    )

firm = {n.strip().lower() for n in config.get('firm_attorneys', [])}
if not firm:
    sys.exit("No firm_attorneys configured; nothing to check against.")

print(f"Firm attorneys: {', '.join(sorted(firm))}")
print(f"Mode: {'APPLY (writes to both stores)' if APPLY else 'dry run'}\n")

memory_db = MemoryDB()
vector_db = VectorDB() if APPLY else None
memories = memory_db.get_all_active()

swaps = []
ambiguous = []

for m in memories:
    oc = (m.get('opposing_counsel') or '').strip().lower()
    sa = (m.get('source_attorney') or '').strip().lower()
    if not oc or oc not in firm:
        continue
    if sa and sa not in firm:
        swaps.append(m)
    else:
        ambiguous.append(m)

print(f"Scanned {len(memories)} memories.\n")

if swaps:
    print(f"INVERTED ({len(swaps)}) -- unambiguous, will be swapped:")
    for m in swaps:
        print(f"  {m['id']}  matter={m.get('matter_id')}  "
              f"judge={m.get('judge')}")
        print(f"      opposing_counsel '{m.get('opposing_counsel')}' "
              f"is one of ours")
        print(f"      source_attorney  '{m.get('source_attorney')}' "
              f"is not -> swap")

if ambiguous:
    print(f"\nAMBIGUOUS ({len(ambiguous)}) -- reported, left alone:")
    for m in ambiguous:
        print(f"  {m['id']}  opposing_counsel="
              f"'{m.get('opposing_counsel')}'  source_attorney="
              f"'{m.get('source_attorney')}'")

if not swaps and not ambiguous:
    print("No attribution inversions found.")
    sys.exit(0)

if not APPLY:
    print(f"\nDry run. Re-run with --apply to write {len(swaps)} swap(s).")
    sys.exit(0)

written = 0
for m in swaps:
    m['opposing_counsel'], m['source_attorney'] = (
        m['source_attorney'], m['opposing_counsel']
    )
    memory_db.save(m)
    # The vector store keeps opposing_counsel in its metadata and is what
    # semantic search filters on. Fixing only SQLite would leave the two
    # stores disagreeing, which is worse than the original error because
    # nothing would ever surface the disagreement.
    vector_db.add(m)
    written += 1
    print(f"  repaired {m['id']}: opposing_counsel is now "
          f"'{m['opposing_counsel']}'")

print(f"\nRepaired {written} memory(s) in both stores.")
