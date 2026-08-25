"""Regression tests for ruling-level evidence counting (issue #22).

Run from the project root, no dependencies beyond the app's own:

    python tests/test_ruling_count.py

Why these exist: extraction splits one ruling into several memories, and
counting those memories as separate evidence inflated confidence and
erased the designed contrast between two judges. Nothing errored when it
was wrong, and nothing would error if it broke again -- which is the
failure mode this project keeps hitting. These assertions are the alarm.

The pure-logic tests always run. The docket tests need the local database
and skip cleanly without it, since `data/` is gitignored.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from retrieval.search_engine import SearchEngine  # noqa: E402

FAILURES = []
SKIPPED = []


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label}" + (f"\n          {detail}" if detail else ""))
        FAILURES.append(label)


def memory(mid, matter, tags, **extra):
    m = {
        'id': mid,
        'matter_id': matter,
        'fact_pattern_tags': list(tags),
        'importance': 'high',
        'confidence': 'verified',
        'memory_type': 'precedent',
        'extraction_category': 'judge_intelligence',
        'practice_area': 'commercial_litigation',
        'judge': 'Test Judge',
        'content': 'test',
        'outcome': 'test',
    }
    m.update(extra)
    return m


engine = SearchEngine(memory_db=None, vector_db=None)


print("\n[1] ruling_key collapses memories describing the same ruling")

same_a = memory('m1', 'CASE-1', ['summary_judgment', 'favored_plaintiff'])
same_b = memory('m2', 'CASE-1', ['summary_judgment', 'favored_plaintiff'])
check(
    "two memories, one ruling -> one key",
    engine.ruling_key(same_a) == engine.ruling_key(same_b),
    f"{engine.ruling_key(same_a)} != {engine.ruling_key(same_b)}"
)

other_matter = memory('m3', 'CASE-2', ['summary_judgment', 'favored_plaintiff'])
check(
    "same ruling shape in a different matter -> different key",
    engine.ruling_key(same_a) != engine.ruling_key(other_matter)
)

other_dir = memory('m4', 'CASE-1', ['summary_judgment', 'favored_defendant'])
check(
    "opposite posture in the same matter and context -> different key",
    engine.ruling_key(same_a) != engine.ruling_key(other_dir)
)

other_cluster = memory('m5', 'CASE-1',
                       ['discovery_hearing', 'favored_plaintiff'])
check(
    "different ruling context -> different key",
    engine.ruling_key(same_a) != engine.ruling_key(other_cluster)
)

no_matter_a = memory('m6', None, ['summary_judgment', 'favored_plaintiff'],
                     source='Transcript A.txt')
no_matter_b = memory('m7', None, ['summary_judgment', 'favored_plaintiff'],
                     source='Transcript B.txt')
check(
    "memories without matter_id fall back to source, not a shared bucket",
    engine.ruling_key(no_matter_a) != engine.ruling_key(no_matter_b)
)


print("\n[2] direction is part of the key, so a ruling group never splits")

groups = {}
for m in [same_a, same_b, other_dir, other_cluster]:
    groups.setdefault(engine.ruling_key(m), []).append(m)
consistent = all(
    len({engine.get_ruling_direction(x) for x in g}) == 1
    for g in groups.values()
)
check(
    "every memory grouped under one key shares one direction",
    consistent
)
check(
    "key's third element is the direction it groups on",
    all(k[-1] == engine.get_ruling_direction(g[0])
        for k, g in groups.items())
)


print("\n[3] _cluster_evidence reports rulings and memories separately")

cluster_input = [
    memory('a1', 'CASE-1', ['summary_judgment', 'favored_plaintiff']),
    memory('a2', 'CASE-1', ['summary_judgment', 'favored_plaintiff']),
    memory('a3', 'CASE-1', ['summary_judgment', 'favored_plaintiff']),
    memory('b1', 'CASE-2', ['summary_judgment', 'favored_plaintiff']),
    memory('c1', 'CASE-3', ['summary_judgment', 'favored_defendant']),
]
records, totals = engine._cluster_evidence(
    cluster_input, [m['id'] for m in cluster_input], "summary judgment"
)

check(
    "3 distinct rulings counted from 5 memories",
    totals['corroborating_count'] + totals['deviating_count'] == 3,
    f"got {totals['corroborating_count']}c + {totals['deviating_count']}d"
)
check(
    "memory total still reported alongside",
    totals['corroborating_memory_count']
    + totals['deviating_memory_count'] == 5,
    f"got {totals['corroborating_memory_count']}"
    f"+{totals['deviating_memory_count']}"
)
check(
    "the lone defendant ruling is the deviation",
    totals['deviating_count'] == 1 and totals['deviating_ids'] == ['c1'],
    f"got {totals['deviating_count']} / {totals['deviating_ids']}"
)
check(
    "every memory ID preserved for traceability",
    sorted(totals['corroborating_ids'] + totals['deviating_ids'])
    == ['a1', 'a2', 'a3', 'b1', 'c1']
)

single_ruling = [
    memory('s1', 'CASE-9', ['summary_judgment', 'favored_plaintiff']),
    memory('s2', 'CASE-9', ['summary_judgment', 'favored_plaintiff']),
    memory('s3', 'CASE-9', ['summary_judgment', 'favored_plaintiff']),
]
records, totals = engine._cluster_evidence(
    single_ruling, [m['id'] for m in single_ruling], "summary judgment"
)
check(
    "3 memories restating one ruling count as 1, not 3",
    totals['corroborating_count'] == 1
    and totals['deviating_count'] == 0
    and totals['corroborating_memory_count'] == 3,
    f"got {totals['corroborating_count']}c/{totals['deviating_count']}d "
    f"from {totals['corroborating_memory_count']} memories"
)
check(
    "and are marked uncompared rather than as agreement",
    records and records[0]['compared'] is False,
    f"got {records[0] if records else 'no records'}"
)


print("\n[4] evidence dict carries every key its consumers read")

CONSUMED_KEYS = [
    # dashboard/app.py and llm_interface/interface.py both read these.
    'entity', 'entity_type', 'confidence_level', 'clusters',
    'corroborating_count', 'deviating_count',
    'corroborating_memory_count', 'deviating_memory_count',
    'corroborating_ids', 'deviating_ids',
]

try:
    from storage.memory_db import MemoryDB
    db = MemoryDB()
    live = db.get_all_active()
except Exception as exc:                      # noqa: BLE001
    live = []
    SKIPPED.append(f"database unavailable ({exc})")

if not live:
    SKIPPED.append("no local database -- docket assertions skipped")
    print("  SKIP  no local database found (data/ is gitignored)")
else:
    live_engine = SearchEngine(db, None)
    reynolds = [m for m in live
                if 'reynolds' in (m.get('judge') or '').lower()]
    ev = live_engine.build_pattern_evidence(
        reynolds, "How does Judge Reynolds rule on summary judgment?"
    )
    missing = {
        k for e in ev.values() for k in CONSUMED_KEYS if k not in e
    }
    check("no consumer key missing from evidence output", not missing,
          f"missing: {sorted(missing)}")
    check(
        "ID list length matches the reported memory count, not the "
        "ruling count",
        all(len(e['corroborating_ids']) == e['corroborating_memory_count']
            and len(e['deviating_ids']) == e['deviating_memory_count']
            for e in ev.values())
    )
    check(
        "rulings never exceed the memories they came from",
        all(e['corroborating_count'] <= e['corroborating_memory_count']
            and e['deviating_count'] <= e['deviating_memory_count']
            for e in ev.values())
    )

    print("\n[5] posture mix tracks the hand count of the transcripts")

    import vocabulary as V
    # Hand count of distinct directional rulings, read off the
    # transcripts in demo_data/. Update only if a transcript changes.
    GROUND_TRUTH = {
        'Reynolds': (11, 9),
        'Kimball': (8, 7),
    }
    TOLERANCE = 3   # residual ambiguity: is SJ on two counts one ruling?

    for judge, (t_plf, t_def) in GROUND_TRUTH.items():
        docket = [m for m in live
                  if judge.lower() in (m.get('judge') or '').lower()]
        if not docket:
            print(f"  SKIP  {judge} not in this database")
            continue
        counts = {}
        for posture in ('favored_plaintiff', 'favored_defendant'):
            counts[posture] = len({
                live_engine.ruling_key(m) for m in docket
                if posture in (set(m.get('fact_pattern_tags') or [])
                               & V.POSTURE_TAGS)
            })
        err = (abs(counts['favored_plaintiff'] - t_plf)
               + abs(counts['favored_defendant'] - t_def))
        check(
            f"{judge}: {counts['favored_plaintiff']}p/"
            f"{counts['favored_defendant']}d vs hand count "
            f"{t_plf}p/{t_def}d (error {err}, tolerance {TOLERANCE})",
            err <= TOLERANCE
        )


print("\n" + "=" * 60)
if SKIPPED:
    for s in SKIPPED:
        print(f"SKIPPED: {s}")
if FAILURES:
    print(f"FAILED: {len(FAILURES)}")
    for f in FAILURES:
        print(f"  - {f}")
    sys.exit(1)
print("All checks passed.")
