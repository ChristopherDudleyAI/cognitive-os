"""
Read-only check: prints the stored fact_pattern_tags (and other tag fields)
for specific memories, straight from the SQLite database. Confirms whether
the posture tags (favored_plaintiff / favored_defendant / favored_neither)
actually landed during ingestion.

This ONLY reads. It writes nothing and changes nothing.

Run from the project root:  python check_tags.py
"""

import sqlite3
import json

DB_PATH = "data/memories.db"

# The Board-complaint exclusion we want to verify (should be favored_defendant),
# plus we'll also show ALL ruling-type memories so you can eyeball every posture tag.
TARGET_ID = "mem_bc94e231"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 70)
print(f"TARGET MEMORY: {TARGET_ID}")
print("=" * 70)

cursor.execute(
    "SELECT id, memory_text, fact_pattern_tags, tags FROM memories WHERE id = ?",
    (TARGET_ID,)
)
row = cursor.fetchone()

if row:
    mem_id, text, fact_tags, tags = row
    print(f"ID: {mem_id}")
    print(f"Text: {text[:120]}...")
    print(f"fact_pattern_tags: {fact_tags}")
    print(f"tags: {tags}")
else:
    print(f"(No memory found with id {TARGET_ID} — it may have a different ID.)")

print()
print("=" * 70)
print("ALL MEMORIES THAT HAVE A POSTURE TAG (favored_*)")
print("=" * 70)

cursor.execute("SELECT id, memory_text, fact_pattern_tags FROM memories")
all_rows = cursor.fetchall()

posture_found = 0
for mem_id, text, fact_tags in all_rows:
    if fact_tags and "favored_" in fact_tags:
        posture_found += 1
        # parse the JSON list so it prints cleanly
        try:
            parsed = json.loads(fact_tags)
        except Exception:
            parsed = fact_tags
        print(f"\n{mem_id}: {text[:70]}...")
        print(f"   tags: {parsed}")

print()
print("=" * 70)
print(f"SUMMARY: {posture_found} of {len(all_rows)} memories carry a favored_* posture tag.")
print("=" * 70)

conn.close()
