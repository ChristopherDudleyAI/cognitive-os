# Cognitive OS — Working Notes

Prototype that turns legal transcripts into a structured, queryable institutional memory for a law firm. Python + Streamlit + SQLite + ChromaDB + Anthropic API. Entry point: `streamlit run dashboard/app.py` **from the project root**.

## The governing rule: accuracy over appearance

**Nothing in this project may be inflated, exaggerated, or altered to make anything look good.** This is a standing instruction from Christopher, not a preference — treat it as binding on every decision.

The product's whole value is that an attorney can rely on what it says. A confidence figure that overstates its evidence is worse than no figure, because it invites reliance it has not earned. Christopher handles persuasion and sales himself; this codebase's only job is to make sure the thing underneath is true.

In practice:

- **Report the honest number even when it is worse.** Confidence dropping from MEDIUM to LOW because the counting was corrected is a fix, not a regression.
- **Never tune thresholds, scoring weights, confidence bands, or the demo data to produce nicer output.** Thin evidence is answered with better evidence, never a softer standard.
- **Separate measured from estimated, and demonstrated from validated,** every time. "One query, one judge" — not an implied generality.
- **Report failures and limitations plainly, including your own.** The most valuable findings here have all been failures that only surfaced by running the system, never by reading it.
- **Correctness before presentation.** UI polish and demo framing come later.

When accuracy and usefulness genuinely diverge — a tool that correctly reports LOW confidence on everything is accurate but not yet useful — **say so**. The fix is better data or a better engine, never a relabelling.

## Read first

- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — durable design constraints. Read before writing code; several fail *silently* if violated.
- **[decision_log.md](decision_log.md)** — *why* past decisions were made. Read before asking why something is built a certain way.
- **Open GitHub Issues** — the roadmap. `gh issue list`
- **[docs/CHARACTER_BIBLE.md](docs/CHARACTER_BIBLE.md)** — required before writing any demo transcript.

## Where things stand

The three-judge demo dataset is the current work. Reynolds has **6** transcripts of a target ~10, Kimball has **4**, Caldwell has **1**. The database holds **183 memories** (Reynolds 112, Kimball 71).

The pipeline works end to end and has been measured, not just assumed: ingest labels persist, `get_by_matter()` returns, the deviation engine reads posture tags, and evidence is now counted by ruling rather than by memory. The open questions are clustering quality and threshold tuning, not whether it runs.

**Known and unfixed — the gap is a defendant shortfall, not a plaintiff lean.** Measured three ways against the Character Bible's own targets:

| judge | actual (p/d/n) | bible target | gap |
|---|---|---|---|
| Reynolds | 46 / 30 / 23 | 45 / 45 / 10 | defendant 15 low, neither 13 high |
| Kimball | 43 / 37 / 18 | 40 / 50 / 10 | defendant 13 low, neither 8 high |

Plaintiff is on target for both. What's missing is defendant-favorable rulings, and too many rulings are landing `favored_neither`. Both dockets need the same correction, so this is a writing habit, not a per-judge problem. It is a transcript problem, not an engine problem.

Note the denominator: quoting plaintiff-vs-defendant alone (Reynolds 60/40) drops `favored_neither` and makes a defendant shortfall look like a plaintiff lean. The bible's targets are three-way — measure them the same way.

Separately, 24 Reynolds memories are mis-tagged `trial_proceeding` from a stray phrase in Reynolds_06; the wording is fixed but the ingested memories still carry it.

Run `python tests/test_ruling_count.py` from the project root before and after touching the evidence engine. No pytest needed.

`python tools/repair_attribution.py` scans stored memories for inverted attorney attribution and repairs unambiguous swaps in both stores. Dry run by default, `--apply` to write. The ingest-time guard only protects memories ingested after it existed, so run this after any bulk ingest.

## Gotchas that will waste your time

- **`config.json` is loaded by relative path.** Run from the project root or it won't be found. Gitignored (live API key); `config.example.json` is the template.
- **`vocabulary.py` is the single source of truth for controlled tags.** `structurer.py` and `search_engine.py` both import from it and reference the *same* frozenset objects. Edit the module, never the instance aliases. Adding a tag also means adding it to the extraction prompt in `extractor.py`, or nothing emits it.
- **The posture rule is tag-triggered, not judgment-triggered.** If `fact_pattern_tags` contains a ruling-type tag it MUST contain a posture tag. Phrasing it as "required on any memory describing a ruling" was measured at 70% compliance; the mechanical form gets 100%. Don't soften it back.
- **`corroborating_count` means rulings; `corroborating_memory_count` means memories.** Never feed a memory count into `calculate_confidence()`, and never show one where a reader would read it as the amount of evidence. One ruling is routinely three memories, and unevenly so — that asymmetry is what erased the contrast between two judges. See ARCHITECTURE §10.
- **`### Confidence Note` is load-bearing in two places.** The prompt in `llm_interface/interface.py` tells the model to emit it; `dashboard/app.py` matches that literal string to parse the section. Change both together or parsing silently stops finding it.
- **`max_tokens` caps thinking AND visible output together.** Models that think by default spend part of the budget before emitting JSON. A ceiling tuned for a non-thinking model truncates the array mid-object. `extraction_max_tokens` defaults to 16000.
- **Ingest labels come from the form, not the model.** `source_type`, `matter_id`, `source`, `date_of_event` are captured in the UI and override anything the extractor emits. Don't add them to the extraction prompt.
- **Adding a database column is safe.** Append to `MemoryDB.EXPECTED_COLUMNS` plus `CREATE TABLE` and `save()` — `migrate_schema()` upgrades existing databases on startup. Append to the *end*; `row_to_dict()` zips it against `SELECT *`.
- **Entity field names (`judge`, `opposing_counsel`, `source_attorney`) are join keys.** Renaming or aliasing one silently kills cross-source pattern detection.
- **Console scripts need `PYTHONIOENCODING=utf-8`** on Windows, or `sys.stdout.reconfigure(encoding='utf-8')`. A cp1252 terminal raises `UnicodeEncodeError` on em-dashes and will kill a script *after* the API call is billed.
- **Retrieval thresholds are unvalidated** — and the values in `config.json` differ from the reasoning that produced them by an accidental transcription slip. Don't treat them as tuned.
- **`Archive Files/`** holds dead one-off scripts. Nothing imports them. Ignore unless asked.

## This project's characteristic bug

**Infrastructure that exists with nothing feeding it.** Found four times: `matter_id` never requested from the prompt, `source` accepted and discarded, `posture_tags` declared and never read, and the provider layer. Each produced no error and no symptom.

Reviewing code shows you *definitions*. When something is described as "already fixed," grep for its **consumers** before believing it.

## Keeping this current

Design decisions come out of conversation, not code — nothing regenerates them. When a session produces a durable decision or finds new disconnected plumbing, write it into `docs/ARCHITECTURE.md` and open an issue **during the session, not at the end of it.** Context runs out before good intentions do.

Append to `decision_log.md` as decisions are made, following the instructions block at its top. Where it disagrees with the code, **the code is correct** — it has drifted before.

Discrete work goes in GitHub Issues, each self-contained enough for a session opening it cold to act on correctly.

Only secrets stay out of the repo: `config.json` (live API key) and `data/` (local databases). Everything else is public.

## Asking before spending

Christopher has asked to be consulted **before every API call that costs money**, with an estimate. Ingestion runs roughly $0.06/transcript on Sonnet 4.6. Local analysis, tests, and `AppTest` runs are free — do those first and exhaust them before proposing a paid run.
