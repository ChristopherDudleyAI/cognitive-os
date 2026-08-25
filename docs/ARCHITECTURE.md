# Architecture — Durable Design Constraints

This file holds design decisions that **shape all future work** on this project. It is not a task list (those live in GitHub Issues) and not a history of why choices were made (that lives in the decision log).

Read this before writing code. If a change would violate something here, that's a deliberate architectural decision and should be discussed, not made silently.

---

## 0. Accuracy governs every other constraint

**Nothing may be inflated, exaggerated, or altered to make output look good.** This is a standing instruction from Christopher, and it outranks everything below it. The reasoning is in the decision log entry of 2026-08-24; the operational form is in `CLAUDE.md`.

What it forbids, concretely, because these are the shapes the temptation actually takes in this codebase:

- **Tuning thresholds, scoring weights, or confidence bands to move a label.** Retrieval thresholds are unvalidated and will eventually be tuned — that tuning must be driven by retrieval quality measured against known-good results, never by which value makes a demo query return a better-looking confidence.
- **Counting the same thing twice to make evidence look deeper.** One ruling described by four memories is one piece of evidence, not four. This is not hypothetical — it is issue #22, and it silently erased the designed contrast between two judges.
- **Shaping the synthetic corpus to flatter the engine.** The demo data exists to test whether the system detects patterns that are really there. Writing transcripts to compensate for a measurement flaw hides the flaw and does not transfer to real documents.
- **Letting a claim outrun its evidence in any user-visible string, doc, or README.** Distinguish measured from estimated, and demonstrated from validated. One query against one judge is exactly that.

When accuracy and usefulness genuinely diverge — a system that correctly reports LOW confidence on everything is accurate but not yet useful — **surface it rather than resolving it quietly.** The response is better data or a better engine, never a relabelling.

## 1. The memory schema is a shared contract

Every extraction path — no matter what kind of document it reads — must emit the same JSON shape. Storage, retrieval, scoring, and clustering all depend on it.

Fields that must be present and identically named on every memory:

| Field | Why it's load-bearing |
|---|---|
| `memory_type` | Drives per-type relevance thresholds in retrieval |
| `extraction_category` | Selects which memories participate in pattern clustering |
| `practice_area`, `matter_type` | Filtering and scoring |
| `importance`, `confidence` | Retrieval scoring weights |
| `outcome` | Scoring, and the label that gives other memories meaning |
| `status`, `permission_level` | Gate what reaches the LLM at all |
| `fact_pattern_tags` | The clustering key — see §4 |
| `judge`, `opposing_counsel`, `source_attorney` | Entity join keys — see §2 |
| `matter_id` | Case-lifecycle linkage — see §3 |

## 2. Entity field names are join keys — never rename or alias them

`judge`, `opposing_counsel`, and `source_attorney` are how `build_pattern_evidence()` groups memories to detect corroboration and deviation. If one extraction branch emits `judge` and another emits `judge_name`, cross-source pattern recognition silently produces nothing — no error, no warning, just missing patterns.

Entity values are whitespace-normalized in `structurer.validate()`. That fixes formatting drift only; it cannot merge `"Hon. Marcus T. Caldwell"` with `"Caldwell"`. **Canonical naming discipline at the source is still required.**

## 3. `matter_id` is the case-lifecycle thread

The entire ambition of tracing a matter from intake through to outcome depends on `matter_id` being populated consistently. The database column, `get_by_matter()`, the ChromaDB metadata filter, and the search-engine parameter all exist and work.

**It cannot be inferred from document text.** An LLM has no way to know a firm's matter numbering. It must be supplied by the human at ingest time.

Retrofitting `matter_id` onto already-ingested memories requires re-ingesting them. Capture it at the door.

## 4. Controlled vocabulary lives in exactly one module

Clustering, deviation detection, and relevance scoring all work by set intersection against fixed tag vocabularies. **All of them are defined in `vocabulary.py` and nowhere else.** `structurer.py` and `search_engine.py` import from it and alias onto instance attributes; edit the module, never the aliases.

The unions are named by **purpose**, not assembled inline at each use site:

| Union | Used by | Contents |
|---|---|---|
| `CONTROLLED_VOCABULARY` | tag validation at ingest | everything |
| `CLUSTERING_TAGS` | `get_context_cluster()` | legal basis + proceeding + strategy |
| `SCORING_TAGS` | the structured-tag bonus in `score_memory()` | everything |
| `FAVORABLE_/UNFAVORABLE_RULING_TAGS` | `get_ruling_direction()` fallback only | ruling-type partition |

Building these inline is what caused the original drift: `POSTURE_TAGS` was added for audit finding #3 and never made it into the scoring union, and `OUTCOME_TAGS` was never defined in `search_engine.py` at all — so memories tagged `favored_plaintiff` or `strategy_succeeded` earned no structured-tag bonus despite the extraction prompt requiring those tags. Nothing errored. The signal was just missing.

`CLUSTERING_TAGS` deliberately excludes ruling type, outcome, and posture. Clustering must group by shared *context* so that direction can then be compared within a cluster; folding outcome into the cluster key would group memories by their result and make every cluster internally consistent by construction.

**Adding a tag** means adding it to `vocabulary.py` *and* to the extraction prompt in `ingestion/extractor.py`, which is what instructs the model to emit it. A tag defined here that the prompt never produces is dead weight; a tag the prompt emits that is missing here fails validation and will not cluster. Per-branch vocabularies belong alongside their branch (§6), not in this module.

## 5. `source_type` and `extraction_category` are different axes

- `extraction_category` = what a memory is **about** (`judge_intelligence`, `attorney_strategy`)
- `source_type` = where it **came from** (court transcript, written order, attorney debrief, email)

Conflating them loses real capability. A `judge_intelligence` memory sourced from a written order is the judge's own stated reasoning; the same category sourced from an attorney debrief is one person's read of a mood. Those should not carry equal weight in retrieval, and they should not be clustered against each other as if directly comparable.

Keeping `source_type` as its own field also produces the labeled dataset a future source-type auto-classifier would need to train on.

## 6. Extraction branches: shared spine, branching taxonomy

Different source types contain fundamentally different intelligence. A court transcript has rulings and objections; an intake call has emotional state and risk tolerance. One universal extraction prompt cannot serve both.

The split:

**Shared across every branch**
- The output JSON contract (§1)
- Entity field names (§2)
- `matter_id` (§3)
- Core extraction rules ("one memory equals one discrete piece", "if a name is mentioned capture it", "be specific and factual, not general")

**Varies per branch**
- The extraction taxonomy — what to look for
- The controlled `fact_pattern_tags` vocabulary for that source type
- Chunk size — an email thread and a 200-page transcript do not chunk alike
- Model selection — dense human judgment deserves a stronger model than mechanical records
- Default `confidence` — see §7

## 7. Confidence should reflect source reliability, not model self-assessment

A court order is `verified` by construction; it is the primary document. An attorney's impression of whether a judge seemed sympathetic is `uncertain` no matter how confidently it is phrased.

Setting `confidence` defaults at the branch level is more honest than asking the model to self-assess, and it costs nothing.

## 8. Fields that must be captured at ingest, not inferred

None of these can be reliably derived from document text, so the ingest form collects all four and they take precedence over anything the model emits:

- **`source_type`** — which extraction branch to route to
- **`matter_id`** — the lifecycle thread (§3)
- **`source`** — which specific document this came from
- **`date_of_event`** — when it happened, not when it was ingested

`source_name`, `matter_id`, and document text are **required**; `date_of_event` is optional and falls back to ingestion time when unknown.

The Source Type dropdown is generated from `Extractor.BRANCHES`, not from a config list, so it can never offer a source type that has no extraction prompt behind it.

**Schema changes are safe to make.** `MemoryDB.migrate_schema()` adds any missing column to an existing database on startup, so introducing a field no longer requires a database reset. Column order is defined once in `MemoryDB.EXPECTED_COLUMNS` and both the migration and `row_to_dict()` derive from it — append new columns to the end of that list rather than inserting mid-list.

## 9. Pattern confidence has a scope limit

The corroboration/deviation engine is sound for **observed behavioral patterns** where the causal link is tight and observations are directly comparable — "this judge sustains foundation objections in depositions."

It is **not** a basis for cross-lifecycle predictive claims — "clients who present as financially pressured settle for less." Those involve many intervening variables and require far more data than a boutique firm generates. Fourteen corroborating observations is strong evidence about a judge's habits and near-meaningless as a predictive claim about client psychology.

If both kinds of claim are ever rendered in the same confidence UI, they must be visually distinguished, or the system will present a small-sample coincidence with the same authority as a well-established pattern.

## 10. Local-first, model-agnostic

Memories are stored as structured data in a local database, not as text baked into a model's context window. The reasoning engine on top should be swappable without rebuilding the knowledge base.

Current state: the code calls the Anthropic API directly. `llm_interface/providers/` exists but is empty. This is a planned direction, not a built feature — do not describe it as implemented.

Note the real gap in the local-first claim: everything stays on the machine except the extraction/query API call itself. For any deployment where document contents genuinely cannot leave the premises, that call is the constraint that matters.

---

## Known disconnected plumbing

Places where infrastructure exists but nothing feeds it. Verify before assuming a feature works:

| What | Status |
|---|---|
| `llm_interface/providers/` | Empty directory. Both `extractor.py` and `interface.py` instantiate `anthropic.Anthropic` directly. |

**Resolved:** `matter_id`, `source`, and `source_type` are now captured by the ingest form and persisted (see §8). `project` was removed rather than wired up — it was unused and speculative. `MemoryDB.get_by_matter()` returns results for the first time.

## Features that were planned but deliberately dropped

- **`bare_query` / Compare mode** — a "with memory vs. without memory" demo path. Discussed in early design notes and referenced in the decision log, but never implemented and no longer wanted. Do not build it.
