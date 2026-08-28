"""Measure each judge's posture profile against the Character Bible.

This is the experiment readout. The claim the whole project rests on is
that structured extraction plus honest counting produces visibly
different profiles for judges who actually differ. This prints the
numbers that either support that or do not.

Everything here is local -- no API calls, free to re-run.

    python tools/measure_docket.py

Two figures appear for every judge and they are not interchangeable:

  by ruling   distinct rulings, deduped by (matter, context, direction).
              This is the evidence count and what confidence is built on.
  by memory   how many extracted memories those rulings came from. Shown
              only so the gap between the two stays visible, because
              quoting it as evidence is exactly what issue #22 was.

The bible's targets are three-way and include favored_neither. Measuring
plaintiff-versus-defendant alone drops the neutrals and turns a defendant
shortfall into an apparent plaintiff lean -- which is a mistake that has
already been made here once and written into three documents before
anyone caught it.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import vocabulary as V                                  # noqa: E402
from retrieval.search_engine import SearchEngine        # noqa: E402
from storage.memory_db import MemoryDB                  # noqa: E402

# Targets as the bible states them: plaintiff / defendant / neither.
TARGETS = {
    'Marcus T. Caldwell': (70, 25, 5),
    'Patricia A. Reynolds': (45, 45, 10),
    'Robert D. Kimball': (40, 50, 10),
}

POSTURES = ('favored_plaintiff', 'favored_defendant', 'favored_neither')

db = MemoryDB()
engine = SearchEngine(db, None)
memories = db.get_all_active()

print(f"{len(memories)} memories in the database\n")

for judge, (tp, td, tn) in TARGETS.items():
    docket = [
        m for m in memories
        if judge.split()[-1].lower() in (m.get('judge') or '').lower()
    ]
    if not docket:
        print(f"{judge}: not in this database\n")
        continue

    matters = {m.get('matter_id') for m in docket if m.get('matter_id')}

    rulings, mems = {}, {}
    for posture in POSTURES:
        tagged = [
            m for m in docket
            if posture in (set(m.get('fact_pattern_tags') or [])
                           & V.POSTURE_TAGS)
        ]
        rulings[posture] = len({engine.ruling_key(m) for m in tagged})
        mems[posture] = len(tagged)

    total = sum(rulings.values())
    if not total:
        print(f"{judge}: no postured rulings\n")
        continue

    def pct(d):
        return {k: round(100 * v / sum(d.values())) for k, v in d.items()}

    r, mm = pct(rulings), pct(mems)
    print(f"{judge}  —  {len(docket)} memories, {len(matters)} matters, "
          f"{total} rulings")
    print(f"  {'':<12}{'plaintiff':>11}{'defendant':>11}{'neither':>10}")
    print(f"  {'by ruling':<12}"
          f"{r['favored_plaintiff']:>10}%{r['favored_defendant']:>10}%"
          f"{r['favored_neither']:>9}%"
          f"   ({rulings['favored_plaintiff']}/"
          f"{rulings['favored_defendant']}/{rulings['favored_neither']})")
    print(f"  {'by memory':<12}"
          f"{mm['favored_plaintiff']:>10}%{mm['favored_defendant']:>10}%"
          f"{mm['favored_neither']:>9}%"
          f"   ({mems['favored_plaintiff']}/"
          f"{mems['favored_defendant']}/{mems['favored_neither']})")
    print(f"  {'bible target':<12}{tp:>10}%{td:>10}%{tn:>9}%")
    gap = (abs(r['favored_plaintiff'] - tp)
           + abs(r['favored_defendant'] - td)
           + abs(r['favored_neither'] - tn))
    print(f"  total deviation from target: {gap} points\n")

# The contrast is the product claim. State it plainly.
present = [j for j in TARGETS
           if any(j.split()[-1].lower() in (m.get('judge') or '').lower()
                  for m in memories)]
if len(present) >= 2:
    print("=" * 60)
    print("CONTRAST — the claim under test\n")
    shares = {}
    for judge in present:
        docket = [m for m in memories
                  if judge.split()[-1].lower()
                  in (m.get('judge') or '').lower()]
        counts = {
            p: len({engine.ruling_key(m) for m in docket
                    if p in (set(m.get('fact_pattern_tags') or [])
                             & V.POSTURE_TAGS)})
            for p in POSTURES
        }
        tot = sum(counts.values()) or 1
        shares[judge] = 100 * counts['favored_defendant'] / tot

    for judge, share in sorted(shares.items(), key=lambda x: -x[1]):
        print(f"  {judge:<24} {share:5.1f}% defendant")

    spread = max(shares.values()) - min(shares.values())
    print(f"\n  spread: {spread:.1f} points")
    if spread >= 15:
        print("  These judges read as different on party posture.")
    elif spread >= 8:
        print("  A difference is present but modest. Whether it is "
              "legible to a\n  reader is a separate question from "
              "whether it is measurable.")
    else:
        print("  These judges do NOT read as meaningfully different on "
              "party posture.\n  The corpus, not the engine, is the "
              "thing to fix.")
