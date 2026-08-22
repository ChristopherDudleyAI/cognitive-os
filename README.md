# Cognitive OS — Legal Intelligence Platform

A prototype for turning legal transcripts (depositions, hearings, client meetings) into a structured, queryable institutional memory for a law firm.

The problem this is aimed at: when an attorney learns something — how a specific judge actually rules on hearsay objections, what worked against a specific opposing counsel, the pattern behind how a certain type of case tends to play out — that knowledge usually lives in one person's head. When they retire or move on, it leaves with them, and the next attorney has to relearn it from scratch. This system pulls that knowledge out of the transcript at the moment it's created and stores it in a form any attorney at the firm can query later, not just the person who was in the room.

It's built around three ideas:

**Experience that transfers, not just data that's stored.** The point isn't only to preserve what a senior attorney knows — it's to make that knowledge usable by someone who wasn't there. A junior associate can query how a judge has actually ruled across years of proceedings, and make a better-informed call without having sat through any of them.

**Front-load the AI cost, don't repeat it.** Instead of having an AI re-read a pile of raw documents every time someone asks a question — slow, expensive, and prone to losing details buried in a big pile of text — this system pays the AI cost once, at ingestion, to turn a transcript into clean, labeled, structured records. After that, answering a question means pulling only the records that clear a relevance bar for that specific question, rather than re-processing everything from scratch.

**Keep the knowledge base independent of any one AI model.** The memories are stored as structured data — judge name, ruling type, confidence level, tags — not as raw text baked into one model's context window, and they live in the firm's own local database rather than inside a vendor's system. That's a deliberate choice: as models improve or get cheaper, the reasoning engine on top should be swappable without rebuilding the knowledge base underneath it. (Current state: the code calls Anthropic's API directly, and there's an empty `llm_interface/providers/` folder meant to eventually hold that provider-swapping layer — a planned direction, not built yet. Worth knowing if you're reading the code rather than just this description.)

On top of that, the retrieval side does something a plain keyword search wouldn't: when you ask a question, it doesn't just find matching memories, it clusters them by context and checks whether they agree with each other. If 9 out of 10 memories say a judge tends to sustain hearsay objections and 1 says the opposite, it surfaces that as a confidence level, with the option to go check the outlier. It's trying to answer "how sure should I be about this pattern" rather than just "here's something that matches."

## Built with

Python · SQLite (structured records) · ChromaDB (vector search) · Streamlit (dashboard) · Anthropic API (extraction and response generation)

## Status

Early-stage, working prototype. Built solo, and iterated on through a lot of trial and error — several of the fixes in this codebase (tag normalization, name normalization, a ChromaDB filter bug, a JSON truncation bug on long transcripts) came from running it against test transcripts and finding out what broke. No seed data ships with the repo, though the system has been tested against a synthetic dataset of fictional judges and cases.

## How it works

```
Transcript pasted in
        ↓
  extractor.py     — sends the text to Claude with a detailed prompt asking it to
                      pull out every distinct piece of legal intelligence, tagged
                      by category (judge behavior, attorney strategy, witness
                      credibility, etc). Long transcripts get chunked automatically.
        ↓
  structurer.py     — validates and normalizes what comes back: fixes inconsistent
                      tag formatting, normalizes names so "Judge  Caldwell" and
                      "Judge Caldwell" don't get treated as different people, and
                      catches tags that don't match the controlled vocabulary
                      pattern-matching depends on.
        ↓
  storage/          — every memory gets saved twice: memory_db.py (SQLite) holds
                      the structured fields, vector_db.py (ChromaDB) holds an
                      embedding for semantic search.
        ↓
  search_engine.py  — on a query, runs semantic search + keyword search + any
                      targeted lookups (by judge, by opposing counsel), merges
                      and scores the results, then clusters same-context memories
                      to work out which ones corroborate each other and which
                      ones are genuine outliers.
        ↓
  llm_interface.py  — hands the scored, clustered memories to Claude with
                      instructions to write a structured brief: direct answer,
                      patterns ranked by confidence, a synthesis, and a confidence
                      note. Memory IDs only show up in a caveat section, never
                      inline, so the response stays readable.
        ↓
  dashboard/app.py  — Streamlit UI with three tabs: ingest a transcript, query the
                      memory bank, or browse everything stored.
```

## Running it

You'll need Python and these packages:

```bash
pip install streamlit anthropic chromadb
```

Copy `config.example.json` to `config.json` and add your own Anthropic API key. `config.json` is gitignored — never commit a real key.

```bash
cp config.example.json config.json
```

Then run from the project root (the app looks for `config.json` in the current directory):

```bash
streamlit run dashboard/app.py
```

The `data/` folder (SQLite + ChromaDB files) gets created automatically on first run.

## Folder layout

- `dashboard/` — the Streamlit UI
- `ingestion/` — pulls structured memories out of raw transcript text
- `retrieval/` — search, scoring, and pattern/deviation detection
- `storage/` — the SQLite and ChromaDB wrappers
- `llm_interface/` — formats retrieved memories into a prompt and calls Claude for the final response
- `Archive Files/` — old one-off debugging/patch scripts, kept for history, not part of the running app

## Known rough edges

- No login or access control — anyone with access to the running dashboard sees everything stored
- No automated tests yet
- Retrieval relevance thresholds (the score a memory needs to reach before it's shown to you) are initial estimates, not yet tuned against real usage
- `dashboard/app.py` handles all three tabs in one file — works fine now, will probably want splitting up as it grows
- Some infrastructure is built but not yet wired up (`matter_id`, source tracking, the provider-swap layer) — see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## Project docs

- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — design constraints that shape future work: the shared memory schema, how extraction branches are meant to split, and which pieces of plumbing are currently disconnected
- **[Issues](../../issues)** — the roadmap, tracked as discrete work items
