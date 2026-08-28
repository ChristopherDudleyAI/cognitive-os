"""Export and restore extracted memories without re-calling the API.

Testing an ingestion or extraction change means wiping the database and
rebuilding it. Rebuilding by re-ingesting costs roughly $0.06 a
transcript, every time, and most changes worth testing are not on the
extraction side at all -- retrieval scoring, clustering, the confidence
engine and the dashboard all consume memories that have already been
extracted and do not care how they got there.

So: snapshot the memories to JSON, wipe, test, restore. Free.

    python tools/snapshot_memories.py --export data/snapshot.json
    python tools/snapshot_memories.py --restore data/snapshot.json

**When a restore is NOT valid.** A snapshot preserves what the extractor
produced at the time it ran. If the thing being tested is the extraction
prompt, a branch, the tag vocabulary, the posture rule, or the structurer
itself, then the whole point is to see different memories come out --
restoring old ones would test nothing and quietly hide the change. Those
runs have to be paid for. Everything downstream of extraction can be
tested off a snapshot.

Snapshots are plain JSON and are worth keeping. `data/` is gitignored, so
a snapshot lives outside version control alongside the databases -- copy
it somewhere durable if it represents a corpus worth not losing.
"""
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from storage.memory_db import MemoryDB        # noqa: E402
from storage.vector_db import VectorDB        # noqa: E402


def usage():
    sys.exit(
        "usage:\n"
        "  python tools/snapshot_memories.py --export <file.json>\n"
        "  python tools/snapshot_memories.py --restore <file.json>\n"
    )


if len(sys.argv) != 3 or sys.argv[1] not in ('--export', '--restore'):
    usage()

mode, path = sys.argv[1], sys.argv[2]
memory_db = MemoryDB()

if mode == '--export':
    memories = memory_db.get_all_active()
    if not memories:
        sys.exit("Database holds no active memories -- nothing to export.")

    judges = sorted({
        m.get('judge') for m in memories
        if m.get('judge') and m['judge'] != 'none'
    })
    matters = sorted({
        m.get('matter_id') for m in memories if m.get('matter_id')
    })

    payload = {
        'exported_at': datetime.now().isoformat(),
        'memory_count': len(memories),
        'judges': judges,
        'matters': matters,
        'memories': memories,
    }
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)

    size_kb = os.path.getsize(path) / 1024
    print(f"Exported {len(memories)} memories to {path} ({size_kb:.0f} KB)")
    print(f"  judges:  {', '.join(judges) or 'none'}")
    print(f"  matters: {len(matters)}")
    print("\nThis snapshot restores without any API calls. It is only "
          "valid for testing\nchanges downstream of extraction -- see the "
          "note at the top of this file.")
    sys.exit(0)

# --- restore ---
if not os.path.exists(path):
    sys.exit(f"No such snapshot: {path}")

with open(path, encoding='utf-8') as fh:
    payload = json.load(fh)

memories = payload.get('memories') or []
if not memories:
    sys.exit(f"{path} contains no memories.")

existing = len(memory_db.get_all_active())
print(f"Snapshot: {len(memories)} memories, taken "
      f"{payload.get('exported_at', 'unknown')}")
print(f"  judges: {', '.join(payload.get('judges') or []) or 'none'}")
print(f"Database currently holds {existing} active memories.")
if existing:
    # Both stores upsert by id, so a restore over a populated database
    # overwrites matching ids and leaves everything else in place. That
    # is a merge, not a clean rebuild, and the difference matters when
    # the point was to test against a known corpus.
    print("\nWARNING: restoring over a populated database merges by id "
          "rather than\nreplacing. For a clean rebuild, wipe first.")

vector_db = VectorDB()
restored = 0
failed = []
for m in memories:
    try:
        memory_db.save(m)
        if m.get('memory_text'):
            vector_db.add(m)
        restored += 1
    except Exception as exc:                  # noqa: BLE001
        failed.append((m.get('id'), str(exc)))

print(f"\nRestored {restored} memories to both stores.")
if failed:
    print(f"FAILED on {len(failed)}:")
    for mid, err in failed[:10]:
        print(f"  {mid}: {err}")
print(f"Database now holds {len(memory_db.get_all_active())} active "
      f"memories, {vector_db.count()} vectors.")
