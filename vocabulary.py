"""Controlled tag vocabulary — the single source of truth.

Clustering and deviation detection work by set intersection against these
vocabularies. They are read at two points in the pipeline:

  - ingestion/structurer.py   validates extracted tags against them
  - retrieval/search_engine.py clusters and scores against them

These lists were previously defined separately in both files. They drifted:
OUTCOME_TAGS existed only in the structurer, and POSTURE_TAGS — added to fix
audit finding #3 — was never added to the retrieval scoring union, so a
memory tagged `favored_plaintiff` or `strategy_succeeded` earned no
structured-tag bonus at all. Nothing errored; the signal was just silently
absent. Defining them once removes that whole class of failure.

ADDING A TAG
------------
Add it to the appropriate set below AND to the extraction prompt in
ingestion/extractor.py, which is what instructs the model to emit it. A tag
here that the prompt never produces is dead weight; a tag the prompt emits
that is missing here fails validation and will not cluster.

Extraction branches may define additional per-branch vocabularies (see
docs/ARCHITECTURE.md section 6). Those belong alongside their branch, not
here — this module holds only tags shared across branches.
"""

# --- Base vocabularies -----------------------------------------------------

# What the court actually did.
RULING_TYPE_TAGS = frozenset({
    'objection_sustained',
    'objection_overruled',
    'motion_granted',
    'motion_denied',
    'evidence_admitted',
    'evidence_excluded',
    'sanctions_issued',
    'discovery_ordered',
})

# The legal ground the ruling turned on.
LEGAL_BASIS_TAGS = frozenset({
    'foundation_objection',
    'speculation_objection',
    'hearsay_objection',
    'assumes_facts_objection',
    'mischaracterization_objection',
    'relevance_objection',
    'daubert_standard',
    'spoliation',
    'privilege_claim',
    'deadline_violation',
    'standard_of_care',
    'causation',
})

# The procedural setting.
PROCEEDING_TAGS = frozenset({
    'deposition_proceeding',
    'motion_hearing',
    'trial_proceeding',
    'summary_judgment',
    'motion_in_limine',
    'discovery_hearing',
})

# The technique an attorney employed.
STRATEGY_TAGS = frozenset({
    'examination_technique',
    'objection_strategy',
    'motion_strategy',
    'argument_framing',
    'witness_impeachment',
    'document_strategy',
    'deadline_management',
})

# Whether it worked.
OUTCOME_TAGS = frozenset({
    'strategy_succeeded',
    'strategy_failed',
    'strategy_partial',
    'tactic_succeeded',
    'tactic_failed',
})

# Which party a ruling actually benefited, judged by effect rather than by
# verb — an objection sustained favors whoever raised it. Added to fix audit
# finding #3, where a judge ruling consistently for different parties read as
# a false deviation.
POSTURE_TAGS = frozenset({
    'favored_plaintiff',
    'favored_defendant',
    'favored_neither',
})


# --- Ruling direction fallback --------------------------------------------
# Used ONLY when a ruling memory carries no posture tag. This partition is
# perspective-fixed and therefore unreliable: "plaintiff's motion granted"
# and "defendant's motion denied" both favor the plaintiff, but the first
# reads as favorable here and the second as unfavorable. That mismatch is
# what audit finding #3 identified, and it is why POSTURE_TAGS exists and
# takes precedence in get_ruling_direction().

FAVORABLE_RULING_TAGS = frozenset({
    'objection_sustained',
    'motion_granted',
    'evidence_excluded',
    'sanctions_issued',
    'discovery_ordered',
})

UNFAVORABLE_RULING_TAGS = frozenset({
    'objection_overruled',
    'motion_denied',
    'evidence_admitted',
})


# --- Purpose-specific unions ----------------------------------------------
# Named by what they are FOR. The previous code built these inline at each
# use site, which is how POSTURE_TAGS came to be missing from one of them.

# Everything. Used to validate extracted tags and warn on drift.
CONTROLLED_VOCABULARY = (
    RULING_TYPE_TAGS
    | LEGAL_BASIS_TAGS
    | PROCEEDING_TAGS
    | STRATEGY_TAGS
    | OUTCOME_TAGS
    | POSTURE_TAGS
)

# Defines the comparison group in get_context_cluster(). Deliberately
# EXCLUDES ruling type, outcome and posture: those describe how a matter came
# out, and clustering must group by shared context first so that direction can
# then be compared within a cluster. Folding outcome into the cluster key
# would group memories by their result and make every cluster look internally
# consistent by construction.
CLUSTERING_TAGS = (
    LEGAL_BASIS_TAGS
    | PROCEEDING_TAGS
    | STRATEGY_TAGS
)

# Earns a memory the structured-tag relevance bonus in score_memory(). Any
# tag from the controlled vocabulary signals a well-structured memory, so
# this is the full vocabulary.
SCORING_TAGS = CONTROLLED_VOCABULARY

# Categories whose memories the clustering engine depends on. Unrecognized
# tags in these are worth warning about at ingest.
TAG_CHECKED_CATEGORIES = frozenset({
    'judge_intelligence',
    'attorney_strategy',
    'opposing_counsel',
    'procedural',
})
