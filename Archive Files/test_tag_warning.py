"""
Deterministic test for the structurer.py fixes (#1 tag drift, #2 name drift).
Bypasses the LLM entirely — feeds hand-crafted candidates straight into the
Structurer so we control exactly what goes in.

This writes NOTHING to the databases. structure() only builds/returns dicts.

Run from the project root:  python test_tag_warning.py
"""

from ingestion.structurer import Structurer

structurer = Structurer()

print("=" * 60)
print("TEST 1 — formatting drift should auto-normalize, NO warning")
print("=" * 60)
print("Input tags: ['Objection Sustained', 'hearsay-objection', '  motion_hearing  ']")
print("Expected: normalizes to objection_sustained / hearsay_objection /")
print("          motion_hearing, and NO [TAG WARNING] prints.")
print("-" * 60)
result1 = structurer.structure({
    "memory_text": "Judge sustained a hearsay objection during the motion hearing.",
    "memory_type": "precedent",
    "extraction_category": "judge_intelligence",
    "fact_pattern_tags": ["Objection Sustained", "hearsay-objection", "  motion_hearing  "],
    "judge": "Hon. Test Judge"
})
print(f"Resulting tags: {result1['fact_pattern_tags']}")
print()

print("=" * 60)
print("TEST 2 — typo + invented tag should TRIGGER a warning")
print("=" * 60)
print("Input tags: ['objecton_sustained', 'judge_seemed_annoyed']")
print("Expected: a [TAG WARNING] line prints listing BOTH tags.")
print("-" * 60)
result2 = structurer.structure({
    "memory_text": "Judge appeared irritated and sustained the objection.",
    "memory_type": "precedent",
    "extraction_category": "judge_intelligence",
    "fact_pattern_tags": ["objecton_sustained", "judge_seemed_annoyed"],
    "judge": "Hon. Test Judge"
})
print(f"Resulting tags: {result2['fact_pattern_tags']}")
print()

print("=" * 60)
print("TEST 3 — descriptive tags on a non-clustering category, NO warning")
print("=" * 60)
print("Input category: client_intelligence, tags: ['client_was_nervous']")
print("Expected: NO [TAG WARNING] — descriptive tags are legitimate here.")
print("-" * 60)
result3 = structurer.structure({
    "memory_text": "Client appeared nervous and uncertain about the timeline.",
    "memory_type": "client",
    "extraction_category": "client_intelligence",
    "fact_pattern_tags": ["client_was_nervous"]
})
print(f"Resulting tags: {result3['fact_pattern_tags']}")
print()

print("=" * 60)
print("TEST 4 — name whitespace normalization (#2)")
print("=" * 60)
print("Input judge: 'Hon.  Marcus   T.  Caldwell' (extra spaces)")
print("Expected: collapses to 'Hon. Marcus T. Caldwell'")
print("-" * 60)
result4 = structurer.structure({
    "memory_text": "Ruling issued.",
    "memory_type": "precedent",
    "extraction_category": "judge_intelligence",
    "fact_pattern_tags": ["motion_granted"],
    "judge": "Hon.  Marcus   T.  Caldwell",
    "opposing_counsel": "  Helena   Cross  "
})
print(f"Resulting judge: '{result4['judge']}'")
print(f"Resulting opposing_counsel: '{result4['opposing_counsel']}'")
print()

print("=" * 60)
print("HOW TO READ RESULTS:")
print("- Test 1: tags should look clean, and NO warning should appear above it")
print("- Test 2: a [TAG WARNING] should have appeared listing both bad tags")
print("- Test 3: NO warning (proves no false alarms on descriptive tags)")
print("- Test 4: names should have single spaces, no leading/trailing spaces")
print("If all four match, both fixes are working.")
print("=" * 60)
