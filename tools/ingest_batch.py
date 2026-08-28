"""Ingest transcripts from demo_data/ingest_manifest.json.

The dashboard ingests one document at a time through a web form. That is
right for a real user and wrong for rebuilding a seventeen-document corpus
after a wipe, which is a routine operation here.

This runs the same pipeline the dashboard does -- extractor, structurer,
both stores -- with the ingest labels read from the manifest instead of
typed into a form.

**This spends money.** Roughly $0.06 a transcript. Dry run by default:

    python tools/ingest_batch.py                       # show plan + cost
    python tools/ingest_batch.py --apply
    python tools/ingest_batch.py --apply --only kimball/Kimball_05

Documents whose matter_id is already in the database are skipped unless
--force is given, so re-running cannot silently double-bill or duplicate
memories. Run tools/check_transcripts.py first; a transcript with a
canonical-name error is cheaper to fix before extraction than after.
"""
import json
import os
import sys

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import cost_tracker                                     # noqa: E402
from ingestion.extractor import Extractor               # noqa: E402
from ingestion.structurer import Structurer             # noqa: E402
from storage.memory_db import MemoryDB                  # noqa: E402
from storage.vector_db import VectorDB                  # noqa: E402

MANIFEST = 'demo_data/ingest_manifest.json'
# Measured, not assumed. The six Kimball 05-10 transcripts averaged
# $0.114 each. The older $0.06 figure came from shorter, thinner
# transcripts; once the bible started budgeting 4-5 directional rulings
# per hearing, extraction produced ~24 memories per document instead of
# ~18 and the cost rose with it. A denser corpus costs more to ingest --
# estimate from the transcripts you actually have, not from history.
COST_PER_DOC = 0.114

APPLY = '--apply' in sys.argv
FORCE = '--force' in sys.argv
ONLY = None
if '--only' in sys.argv:
    ONLY = sys.argv[sys.argv.index('--only') + 1]

try:
    with open('config.json') as fh:
        config = json.load(fh)
except FileNotFoundError:
    sys.exit("config.json not found -- run from the project root.")

with open(MANIFEST, encoding='utf-8') as fh:
    manifest = json.load(fh)

docs = [d for d in manifest['documents']
        if not ONLY or ONLY.replace('\\', '/') in d['file']]
if not docs:
    sys.exit(f"No manifest entries match --only {ONLY}")

memory_db = MemoryDB(db_path=config['db_path'])
known_matters = {
    m.get('matter_id') for m in memory_db.get_all_active()
}

planned, skipped = [], []
for d in docs:
    if not os.path.exists(d['file']):
        sys.exit(f"Missing transcript: {d['file']}")
    if d['matter_id'] in known_matters and not FORCE:
        skipped.append(d)
    else:
        planned.append(d)

print(f"Manifest: {len(manifest['documents'])} documents, "
      f"{len(docs)} selected\n")

if skipped:
    print(f"Already ingested, skipping {len(skipped)} "
          f"(--force to re-ingest):")
    for d in skipped:
        print(f"  {d['matter_id']}  {os.path.basename(d['file'])}")
    print()

if not planned:
    print("Nothing to ingest.")
    sys.exit(0)

print(f"To ingest ({len(planned)}):")
for d in planned:
    print(f"  {d['matter_id']}  {os.path.basename(d['file'])}")

estimate = len(planned) * COST_PER_DOC
print(f"\nEstimated cost: ${estimate:.2f} "
      f"({len(planned)} x ~${COST_PER_DOC:.2f})")
print(f"Spend so far:   ${cost_tracker.totals()['total_usd']:.4f}")

if not APPLY:
    print("\nDry run. Re-run with --apply to ingest.")
    sys.exit(0)

extractor = Extractor(
    api_key=config['anthropic_api_key'],
    model=config['model'],
    ingestion_model=config['ingestion_model'],
    max_tokens=config.get('extraction_max_tokens', 16000),
    effort=config.get('extraction_effort'),
)
structurer = Structurer(
    default_project=config['default_project'],
    firm_attorneys=config.get('firm_attorneys', []),
)
vector_db = VectorDB(db_path=config['chroma_path'])

before = cost_tracker.totals()['total_usd']
total_saved = 0

for i, d in enumerate(planned, 1):
    name = os.path.basename(d['file'])
    print(f"\n[{i}/{len(planned)}] {name}")
    text = open(d['file'], encoding='utf-8').read()

    candidates = extractor.extract(text, source_type=d['source_type'])
    if not candidates:
        print("  no memories extracted -- skipping")
        continue

    structured = structurer.structure_batch(
        candidates=candidates,
        source=d['source'],
        source_type=d['source_type'],
        matter_id=d['matter_id'],
        date_of_event=d['date_of_event'],
    )

    saved = 0
    for memory in structured:
        try:
            memory_db.save(memory)
            vector_db.add(memory)
            saved += 1
        except Exception as exc:                        # noqa: BLE001
            print(f"  failed to save {memory.get('id')}: {exc}")
    total_saved += saved
    print(f"  {saved} memories stored")

after = cost_tracker.totals()['total_usd']
print(f"\n{'=' * 56}")
print(f"Stored {total_saved} memories from {len(planned)} document(s).")
print(f"This run cost ${after - before:.4f} "
      f"(estimated ${estimate:.2f}).")
print(f"Running total: ${after:.4f}")
print(f"Database now holds {len(memory_db.get_all_active())} memories.")
print("\nRun tools/repair_attribution.py next -- the ingest guard only "
      "catches\ninversions it can see, and a bulk run is where they "
      "show up.")
