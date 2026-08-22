# Cognitive OS — Working Notes

Prototype that turns legal transcripts into a structured, queryable institutional memory. Python + Streamlit + SQLite + ChromaDB + Anthropic API. Entry point: `streamlit run dashboard/app.py` from the project root.

## Read first

- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — durable design constraints. Read before writing code; several of them fail *silently* if violated.
- **Open GitHub Issues** — the roadmap. `gh issue list`

## Gotchas that will waste your time

- **`config.json` is loaded by relative path.** The app must be run from the project root or it won't find it. The file is gitignored (contains a live API key); `config.example.json` is the template.
- **Three pipes are built but disconnected.** `matter_id` is never requested from the extraction prompt (always `None`, so `get_by_matter()` always returns nothing). `source` and `project` are accepted by `structurer.structure()` and silently discarded. `llm_interface/providers/` is empty — the code calls Anthropic directly. Don't assume these work because the plumbing is there.
- **The controlled tag vocabulary is duplicated** in `ingestion/structurer.py` and `retrieval/search_engine.py`. Adding a tag to one and not the other breaks clustering with no error.
- **Entity field names (`judge`, `opposing_counsel`, `source_attorney`) are join keys.** Renaming or aliasing one silently kills cross-source pattern detection.
- **`Archive Files/`** holds dead one-off debugging scripts. Nothing imports them. Ignore unless asked.
- **Retrieval thresholds** (`memory_type_thresholds` in config) are untested estimates, not tuned values. Don't treat them as validated.

## Keeping this current

The design decisions in `docs/ARCHITECTURE.md` come out of conversation, not out of the code — nothing can regenerate them automatically. When a session produces a durable design decision or finds a new piece of disconnected plumbing, write it into ARCHITECTURE.md and open an issue for the work, **during the session, not at the end of it.** Context runs out before good intentions do.

Discrete work goes in GitHub Issues. Write each one self-contained — file paths, what's broken, what the fix looks like — so a session opening it cold with no memory of the discussion can act on it correctly.

`decision_log.md` (maintained separately, outside this repo) records *why* past decisions were made. Where it disagrees with the code, **the code is correct** — the log is hand-maintained across sessions and has drifted before.
