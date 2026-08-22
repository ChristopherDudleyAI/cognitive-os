# Cognitive OS — Decision Log

**Purpose:** This file is the permanent record of WHY decisions were made on this project — not what was built (that's the handoff packet) and not what's next (that's the roadmap). Just the reasoning behind each real decision, in chronological order, so no future conversation has to guess or reconstruct it.

**Rule for every entry:** If the reasoning is genuinely known and confirmed, write it as fact. If it was inferred, assumed, or never actually validated, say so explicitly. Never let an entry sound more certain than it actually is.

**How this file grows:** Append only. Don't edit or delete old entries once confirmed — if a decision later changes, add a new entry that references and supersedes the old one. Keep entries in date order, oldest first.

---

## INSTRUCTIONS FOR ANY AI READING THIS FILE

This file lives at the project root (`decision_log.md`) and is **committed to the public repository**. Only secrets are kept out of the repo — API keys (`config.json`) and local database files (`data/`). If you are an AI assistant working in this project:

1. **Read this file before assuming you need to ask why something was built a certain way.** Check here first — the reasoning may already be recorded.
2. **Write entries during the session, as decisions are made — not batched at the end.** You have write access to this file; append directly. Batching to end-of-session was the previous process and it failed in practice: context ran out before the writing happened, and the log drifted out of sync with the code (see the 2026-08-22 entry superseding it). If a decision is made at minute ten, log it at minute ten.
3. **Never backfill a WHY with a guess.** If the reasoning wasn't actually stated by Christopher or doesn't otherwise exist in the conversation, write "not recorded" or mark the entry STATUS: inferred/unverified and say so plainly. An invented-sounding justification is worse than an honest gap.
4. **Append only.** Never edit or delete a prior entry. If a decision changes later, add a new entry referencing which prior entry it supersedes. (This instructions block is operational guidance, not a historical record — it may be edited when the process itself changes.)
5. **Know which document to use.** Three layers, and putting something in the wrong one is how information gets lost:
   - **This file** — *why* a decision was made. Append-only, chronological, permanent.
   - **`docs/ARCHITECTURE.md`** (in the repo) — durable design *constraints* that shape future work. Read before writing code.
   - **GitHub Issues** — discrete *work items*. `gh issue list`. Write each self-contained.
6. **Where the code and this file disagree, the code is correct.** This log is hand-maintained across sessions and has drifted before. Verify claims about implementation status against the source before relying on them.

---

## ENTRY TEMPLATE (copy this block for each new entry)

```
### DECISION: [short name of the decision]
DATE: [date decision was made, or "unknown" if lost to history]
STATUS: [confirmed | inferred/unverified | superseded by entry above]

WHAT WAS DECIDED:
[One or two sentences. Plain statement of the choice made.]

WHY:
[The actual reasoning. If this is a real, confirmed reason, state it plainly.
If this is inferred or was never tested/confirmed, say that explicitly —
e.g. "This was a design assumption, not validated with real data."]

ALTERNATIVES CONSIDERED (if known):
[What else was on the table, and why it was rejected, if known. Otherwise write "not recorded."]

STILL OPEN / NEEDS REVISITING:
[Anything about this decision that's unresolved, provisional, or flagged for
future review. Otherwise write "none."]
```

---

## DECISION LOG ENTRIES

*(Oldest first. Phase 1 = original generic Cognitive OS, pre-law-firm-pivot. Phase 2 = law firm rebuild. Phase 3 = live working session, June 16–17 2026.)*

---

## PHASE 1 — ORIGINAL GENERIC COGNITIVE OS (pre-pivot)

---

### DECISION: Local-first architecture over cloud-hosted
DATE: unknown (pre-dates earliest logged conversation)
STATUS: confirmed

WHAT WAS DECIDED:
The entire Cognitive OS system — database, vector store, and memory — runs on local hardware rather than any cloud service. No data leaves the machine unless explicitly sent to an LLM API for reasoning.

WHY:
The core thesis is that AI models are commoditizing while the memory/context layer is the durable asset. Local-first storage gives the user genuine data ownership and privacy that cloud-hosted competitors structurally cannot match without dismantling their own business model. This is also the foundation of the data sovereignty pitch to regulated industries (legal, healthcare, finance).

ALTERNATIVES CONSIDERED (if known):
Not recorded — this appears to have been a founding premise of the project rather than a choice made between options during the logged conversations.

STILL OPEN / NEEDS REVISITING:
none

---

### DECISION: LLM is treated as a replaceable component, not the core asset
DATE: unknown (pre-dates earliest logged conversation)
STATUS: confirmed

WHAT WAS DECIDED:
The system architecture isolates the LLM behind a provider interface (`llm_interface/interface.py`) so that Claude, GPT, Gemini, or local models can be swapped via configuration rather than rebuilding the system.

WHY:
Stated directly and repeatedly: "The LLM is replaceable. The continuity layer is the true asset." The business thesis depends on the memory/retrieval layer being the durable product, not whichever model happens to be best this year.

ALTERNATIVES CONSIDERED (if known):
Not recorded.

STILL OPEN / NEEDS REVISITING:
Currently only Claude is actually implemented as a working provider. OpenAI and Ollama exist as config stubs but are not built out. Adding a new provider (e.g. Gemini) requires writing one new file matching the `BaseLLMProvider` contract — confirmed as low-effort but not yet done for any provider beyond Claude.

---

### DECISION: Build personal demo before seeking technical partner or funding
DATE: unknown (stated early in build process)
STATUS: confirmed

WHAT WAS DECIDED:
Christopher will build and validate a working demo himself (with AI-assisted coding) on his own experience before approaching investors or hiring technical help.

WHY:
Limited funds available. A working demo that visibly shows the gap between memory-enriched and bare LLM responses is worth more to an investor conversation than a pitch deck alone, and validates the core product thesis before spending money.

ALTERNATIVES CONSIDERED (if known):
Hiring a technical co-founder or developer first — rejected due to budget constraints.

STILL OPEN / NEEDS REVISITING:
none — this phase is in progress and proceeding as planned.

---

### DECISION: Six-category memory schema (people, resources, risk, relationships, patterns, context)
DATE: unknown (design phase, pre-build)
STATUS: inferred/unverified — superseded by the law-specific schema (see Phase 2 entry "New memory schema with law-specific fields")

WHAT WAS DECIDED:
Every memory in the system is classified into one of six categories as its primary organizing dimension.

WHY:
Not explicitly justified in the conversation beyond the claim that "every position uses all six" categories regardless of industry. This was presented as a baseline framework reasoning rather than something tested against real organizational data. It has not been validated with actual cross-industry use.

ALTERNATIVES CONSIDERED (if known):
Not recorded.

STILL OPEN / NEEDS REVISITING:
Superseded — this taxonomy was replaced entirely once the law-firm pivot happened. Left here for historical record only.

---

### DECISION: Validation gate (human approval) on every ingested memory, no auto-approval
DATE: unknown (design phase, pre-build)
STATUS: confirmed — superseded by the law-firm-phase decision to use confidence tiering instead (see Phase 2 entry "No approval queue for extracted memories")

WHAT WAS DECIDED:
No memory is written to the database without explicit human approval (Approve, Edit, Flag, or Reject) at ingestion time.

WHY:
Stated directly: this "trains your instinct for what good memory looks like and prevents garbage entering the system before hygiene automation exists." Also positioned as a security/quality control layer in place of an automated approval pipeline.

ALTERNATIVES CONSIDERED (if known):
Auto-approval with later cleanup — implicitly rejected in favor of gatekeeping at the point of entry.

STILL OPEN / NEEDS REVISITING:
Superseded for the law-firm phase. Left here for historical record only.

---

### DECISION: Memory hygiene resolved through human-led "Cognitive Health Review" sessions, not pure automation
DATE: during business-plan discussion (date not stated)
STATUS: confirmed

WHAT WAS DECIDED:
Conflict detection (e.g. contradictory memories) runs automatically in the background, but resolution happens in scheduled in-person/human sessions rather than an automated self-serve scan.

WHY:
Two reasons, both stated explicitly by Christopher and validated in the response: (1) commercial/marketing value — in-person review signals security and seriousness to enterprise buyers; (2) the review conversation itself surfaces new intelligence that an automated scan cannot capture ("is this still true?" prompts new disclosures). This was identified as a genuine dual-purpose insight, not just a marketing trick.

ALTERNATIVES CONSIDERED (if known):
Fully automated hygiene scan with no human involvement — considered and explicitly rejected as lower-value, both technically and commercially.

STILL OPEN / NEEDS REVISITING:
The underlying automated conflict-detection mechanism (semantic similarity + contradiction flagging) is designed conceptually but not yet implemented in code.

---

### DECISION: Physical deployment model — per-position encrypted SSD devices
DATE: during business-plan discussion (date not stated)
STATUS: confirmed (as a design intent; not yet implemented)

WHAT WAS DECIDED:
The long-term commercial product ships as physical encrypted SSDs, one per critical organizational position, rather than purely as software/cloud access.

WHY:
Framed as both a technical and commercial decision. Technically: the local-first architecture already makes a portable device the natural deployment target with minimal rework (relative file paths, self-contained SQLite/ChromaDB). Commercially: handing someone a physical device "that represents organizational sovereignty" is a stronger sell than a software license, and creates an intuitive succession-handoff story (device transfers to a replacement when someone leaves the role).

ALTERNATIVES CONSIDERED (if known):
Pure cloud SaaS — implicitly rejected as conflicting with the data sovereignty positioning. Pure on-machine software install (no dedicated device) — not explicitly discussed as a rejected alternative, but the physical-device framing was clearly preferred for the "tangible artifact" sales argument.

STILL OPEN / NEEDS REVISITING:
Not yet built. Open technical question (acknowledged directly): host-machine dependency — a position's SSD still needs Python/Docker on whatever machine it's plugged into unless the runtime itself is packaged onto the drive. Docker-based packaging was proposed as the cleanest fix but not implemented or tested.

---

### DECISION: Backup architecture — "filing cabinet" model with isolated per-position folders on a master local drive
DATE: during business-plan discussion (date not stated)
STATUS: confirmed (as a design intent; not yet implemented)

WHAT WAS DECIDED:
Each position's device backs up to its own isolated folder on a larger local master drive (not a shared pool), so no position's memory ever mingles with another's, and a lost/failed device can be restored from backup with zero cross-contamination.

WHY:
Christopher proposed this directly as a practical solution to the backup problem inherent in physical-device deployment. The isolation requirement matters because position devices are meant to reflect one specific person/role's cognitive framework — mixing them would defeat the purpose.

ALTERNATIVES CONSIDERED (if known):
Cloud-based encrypted backup — not selected; not deeply discussed, but appears inconsistent with the no-data-leaves-the-building positioning.

STILL OPEN / NEEDS REVISITING:
Not yet implemented in code. No tooling exists yet for the actual mirror/backup process.

---

### DECISION: Extracted memories must preserve the source's original worldview/framing, not be neutralized to generic principles
DATE: during KJV ingestion testing (date not stated)
STATUS: confirmed — superseded the initial extractor behavior; carried forward into the law-firm rebuild's extraction prompt

WHAT WAS DECIDED:
The extraction prompt was changed so that biblical, philosophical, or otherwise worldview-specific source material keeps its original theological/philosophical framing in the stored memory text, rather than being rewritten into belief-neutral generic wisdom.

WHY:
Initial extractor output rewrote "the fear of the LORD" as "reverence toward something greater than yourself," sanitizing the religious framing. Christopher's stated reasoning: the cognitive framework is meant to be personal and authentically reflect how the actual person (or, for a future position-device, the role's actual occupant) thinks — sanitizing it defeats the purpose of building a genuine "cognitive twin" rather than a generic knowledge base. He explicitly connected this to the per-position device thesis: each device should be "more personable to each person" rather than uniformly neutral.

ALTERNATIVES CONSIDERED (if known):
Keep the original sanitized/generic extraction behavior — explicitly rejected after the test run revealed it stripped the religious framing from a Proverbs verse.

STILL OPEN / NEEDS REVISITING:
This is currently the global default behavior of the extractor for all source types. Whether sanitized-vs-worldview-preserving extraction should be a configurable setting per deployment (e.g. for a client who explicitly wants neutral knowledge) has not been discussed.

---

### DECISION: Extractor must attempt outcome detection on conversational/transcript input
DATE: during sales-call ingestion testing (date not stated)
STATUS: confirmed

WHAT WAS DECIDED:
The extraction prompt was expanded so that for conversational content (sales calls, meetings, negotiations), the extractor attempts to identify whether each technique/decision produced a positive, negative, or neutral response, and records that as part of the memory's outcome field, with a confidence level (verified/probable/uncertain).

WHY:
Christopher's stated goal: if a salesperson uploads a call recording, the system should be able to determine whether specific moments in the call resulted in a positive or negative customer reaction, not just log that a technique was used. This makes stored sales memories verified patterns rather than generic tips.

ALTERNATIVES CONSIDERED (if known):
Not recorded — no alternative approach to outcome capture was discussed.

STILL OPEN / NEEDS REVISITING:
Outcome detection has only been tested against fictional, deliberately-positive sales call transcripts. It has not yet been tested against a real, mixed-outcome (some wins, some losses) transcript.

---

### DECISION: Fictional sales-call training material is intentionally biased toward positive outcomes during demo-building phase
DATE: during sales-call ingestion testing (date not stated)
STATUS: confirmed

WHAT WAS DECIDED:
Fictional sales calls generated to test/seed the memory system are deliberately written so that every technique succeeds and every customer response is positive and clear, while still being grounded in real, named sales principles (primarily Hormozi's frameworks).

WHY:
Christopher's stated reasoning: for demo purposes, a memory bank full of clean, confident, directional patterns produces more impressive and more useful guidance than a realistic mixed bag of wins/losses would. The explicit tradeoff was acknowledged: this approach is appropriate for demo-building but would need to be balanced with real wins/losses/near-misses before real production use, because a purely-positive memory bank risks producing overconfident advice in real-world deployment.

ALTERNATIVES CONSIDERED (if known):
Realistic mixed-outcome fictional calls — considered and explicitly deferred to a later (production) phase rather than rejected outright.

STILL OPEN / NEEDS REVISITING:
Flagged directly: this approach should not carry into commercial/production use without correction. Needs revisiting before any real client deployment.

---

### DECISION: Switch default LLM model from Opus to Sonnet for build/demo phase
DATE: during build, after initial successful launch (date not stated)
STATUS: confirmed

WHAT WAS DECIDED:
`config.json` model field changed from `claude-opus-4-5` to `claude-sonnet-4-6` for all system operations during the development/demo phase.

WHY:
Cost. Sonnet is significantly cheaper per token while being more than sufficient for memory extraction, retrieval reranking, and context-enriched response generation — none of which require Opus-level reasoning depth. Confirmed directly that retrieval quality is unaffected by this change because retrieval scoring/ranking happens entirely in local Python code (ChromaDB + custom scoring), not in the LLM call.

ALTERNATIVES CONSIDERED (if known):
Keep using Opus throughout build/demo — rejected due to unnecessary cost at this stage; Opus may be reconsidered for production use later, not decided either way.

STILL OPEN / NEEDS REVISITING:
none for current phase.

---

### DECISION: Bare-query (no-memory-context) comparison feature exists only for demo purposes and must be removed before commercial release
DATE: during build, when llm_interface/interface.py was first written (date not stated)
STATUS: confirmed

WHAT WAS DECIDED:
The system includes a `bare_query` method that sends a prompt to Claude with zero memory context, used solely to generate the "without memory" side of the Compare-mode gap demonstration. This feature is explicitly flagged to be deleted before any commercial/client-facing release.

WHY:
Stated directly: a client's cognitive system should always reason from accumulated memory in real use; the bare-query path has no legitimate place in a production deployment and represents a potential security/quality bypass of the memory layer if left in.

ALTERNATIVES CONSIDERED (if known):
Not recorded — no alternative to outright removal was discussed.

STILL OPEN / NEEDS REVISITING:
Not yet removed — explicitly deferred until commercialization phase. Logged as an open action item, not yet executed.

---

### DECISION: Ingest-mode UI must auto-dismiss a memory card immediately after Approve/Flag/Reject
DATE: during build, after initial dashboard testing (date not stated)
STATUS: confirmed — implemented (the underlying approval-queue concept this UI served was later superseded in the law-firm phase, but this was the state of the generic-phase UI)

WHAT WAS DECIDED:
The dashboard's review-memories flow was changed so that once a candidate memory is approved, flagged, or rejected, it immediately disappears from view (via a `dismissed` set in session state) rather than requiring the user to scroll past already-handled cards to reach the next one.

WHY:
Christopher identified the original behavior (all candidates shown expanded simultaneously, approved ones remaining visible) as clunky and an unnecessary UX friction point, especially anticipating higher memory volumes going forward.

ALTERNATIVES CONSIDERED (if known):
Not recorded — no alternative UI pattern was discussed; the fix (filter dismissed items out of the rendered list, add a remaining-count caption, and a "Start New Ingest" completion state) was implemented directly as proposed.

STILL OPEN / NEEDS REVISITING:
none — implemented and confirmed working in testing.

---

### DECISION: Response format should be concise-first with reasoning available on request, not volunteered
DATE: stated during late-session feedback after the pricing-comparison test (date not stated)
STATUS: confirmed as a design requirement — NOT YET IMPLEMENTED in code

WHAT WAS DECIDED:
Claude's responses inside the system should answer the user's actual question directly and only include supporting context/personal-background references when they directly serve the answer. Complex questions can still warrant long, complex answers — the constraint is about relevance and unrequested context, not arbitrary brevity. An "elaborate on request" follow-up pattern was proposed for surfacing the reasoning behind an answer without including it by default.

WHY:
Identified directly: when the system retrieved a context packet for a pricing question, the response inappropriately surfaced unrelated background facts (e.g. Christopher's plumbing background) just because those memories scored into the top-N retrieved results. Christopher correctly diagnosed this as partly a sparse-data artifact (too few memories at the time, so background memories won retrieval slots by default) and partly a genuine prompting problem (the LLM should filter what it surfaces even when given the context). Both causes were confirmed as real and not mutually exclusive.

ALTERNATIVES CONSIDERED (if known):
Simply shortening all responses regardless of question complexity — explicitly rejected by Christopher ("I do not think the answer is limiting the size of the response... complex questions require complex answers"). The agreed direction is relevance-filtering, not length-capping.

STILL OPEN / NEEDS REVISITING:
Not yet implemented as of the generic-phase work. (Note: the law-firm phase's "locked response structure" and tone-instruction work, below, addresses a closely related wordiness problem but for the legal-brief response format specifically — worth confirming whether this original relevance-filtering instruction was ever folded into that later prompt.)

---

### DECISION: Token cost will be managed via smarter retrieval scoring at scale, not by shortening responses
DATE: same session as the response-format decision above (date not stated)
STATUS: confirmed as a design requirement — superseded in mechanism by the law-firm phase's threshold-and-token-budget system (see Phase 3 entry "Replace the hard 8-memory retrieval cap...")

WHAT WAS DECIDED:
As the memory database grows, the plan for controlling per-query token cost is to tighten retrieval scoring thresholds (so only genuinely high-scoring memories enter the context packet) and enforce a hard token budget cap on the assembled context packet — rather than instructing the LLM to produce shorter answers.

WHY:
Christopher observed token cost trending upward as memory volume increased and was concerned this would compound badly at scale. The diagnosis confirmed: the existing retrieval engine already capped at a fixed top-6 memories, but did not yet scale its scoring strictness as the candidate pool grows.

ALTERNATIVES CONSIDERED (if known):
Limiting response length to control cost — explicitly rejected for the same reason as the response-format decision above (conflated relevance with brevity).

STILL OPEN / NEEDS REVISITING:
Superseded — this exact mechanism (relevance threshold + token budget) was actually built during the law-firm rebuild session. See Phase 3.

---

## PHASE 2 — LAW FIRM PIVOT / REBUILD

---

### DECISION: Pivot product niche to law firms specifically
DATE: unknown (early in project, before June 16 2026 session)
STATUS: confirmed

WHAT WAS DECIDED:
Cognitive OS was repositioned from a general-purpose "Cognitive Operating System" for any organization into a niche product specifically for boutique and mid-sized law firms (5-50 attorneys), branded as "Continuity Infrastructure."

WHY:
Christopher identified that law firms are a strong wedge market: court transcripts and depositions are a naturally rich, structured, and already-existing data source; the pain (partner retirement causing institutional knowledge loss) is acute and well understood by the buyer; the buyer (managing/founding partner) has budget and a clear reason to pay premium fees; the firm's privacy and succession concerns map well onto the product's "preserve and compound knowledge" value proposition.

ALTERNATIVES CONSIDERED (if known):
General executive/multi-industry market — explicitly rejected per the strategic context document ("Previous: General executive market, Multiple industries" → "Current focus: Boutique and mid-sized law firms").

STILL OPEN / NEEDS REVISITING:
None — this pivot is treated as settled direction going forward.

---

### DECISION: Position as "Continuity Infrastructure," not an AI assistant/chatbot/legal research tool
DATE: unknown (part of the same strategic pivot as above)
STATUS: confirmed

WHAT WAS DECIDED:
The product is explicitly positioned as Institutional Knowledge Infrastructure / Continuity Infrastructure — not as an AI assistant, AI agent, chatbot, or legal research platform. It is meant to sit above existing practice management tools (e.g., Clio) as an "Organizational Intelligence Layer," not replace them.

WHY:
Stated directly in the strategic context document: positioning as "AI assistant" or "legal research" would put Cognitive OS in direct competition with large, well-funded players (Harvey, Lexis, Thomson Reuters) — a fight it would lose. Positioning as continuity/succession infrastructure is a different category entirely, tied to a pain point (knowledge loss at retirement) that those competitors don't address.

ALTERNATIVES CONSIDERED (if known):
"AI lawyer" / "legal chatbot" / "legal research platform" positioning — explicitly rejected in the strategic document under "Do NOT position as."

STILL OPEN / NEEDS REVISITING:
None.

---

### DECISION: Reset both databases (SQLite + ChromaDB) when pivoting to the law-firm-specific schema
DATE: June 2026 (start of the rebuild session)
STATUS: confirmed

WHAT WAS DECIDED:
All existing generic memories (KJV Proverbs, Meditations, sales call examples, etc.) were discarded. Both `memories.db` and the `chroma.db` folder were deleted and rebuilt from scratch with a new law-specific schema.

WHY:
Christopher stated directly that the prior memory content "do[es] not matter" for the law-firm pivot and that the priority was rebuilding retrieval and memory classification around legal use cases rather than retrofitting old generic memories into the new schema.

ALTERNATIVES CONSIDERED (if known):
Migrating/converting old generic memories into the new schema — not seriously considered; explicitly waved off by Christopher in favor of a clean reset.

STILL OPEN / NEEDS REVISITING:
None for this reset. (Note: a second, later reset also happened mid-session after partial/broken transcript ingestions polluted the data — see Phase 3 entry "Second database reset.")

---

### DECISION: Reuse existing tooling (SQLite, ChromaDB, Streamlit, Anthropic API) rather than rebuild the stack
DATE: June 2026 (start of rebuild session)
STATUS: confirmed

WHAT WAS DECIDED:
Kept SQLite + ChromaDB storage layer, Streamlit dashboard, Anthropic API interface, and the ingestion/extraction pipeline pattern as-is. Only the schema, extraction prompt, structurer, and retrieval scoring logic were rebuilt to be law-specific.

WHY:
Christopher stated explicitly: "It is fine to reuse all the different tools... The biggest update would be to retrieval and memory classification[;] the dashboard is fine for now."

ALTERNATIVES CONSIDERED (if known):
Rebuilding the stack with different storage/UI tools — not considered; explicitly ruled out by Christopher.

STILL OPEN / NEEDS REVISITING:
None.

---

### DECISION: New memory schema with law-specific fields
DATE: June 2026 (rebuild session)
STATUS: confirmed

WHAT WAS DECIDED:
Memory schema expanded beyond the generic version to include: memory_type (matter, client, precedent, partner_judgment, operational), practice_area, matter_type, matter_id, extraction_category, outcome, source_attorney, opposing_counsel, judge, fact_pattern_tags, confidence, status, permission_level, importance, tags.

WHY:
Designed jointly by Claude and Christopher to map onto how lawyers actually reason about cases — by judge, by opposing counsel, by matter type, by outcome — rather than the generic people/resources/risk/relationships/patterns/context categories used in the original Cognitive OS.

ALTERNATIVES CONSIDERED (if known):
Keeping the original generic category schema (people, resources, risk, relationships, patterns, context) — implicitly rejected in favor of the legal-specific taxonomy; not explicitly debated, just superseded.

STILL OPEN / NEEDS REVISITING:
None on the schema itself. (The 110-item extraction taxonomy built from this schema is itself flagged for future expansion — see "Use a 110-item extraction taxonomy" entry below.)

---

### DECISION: Use a 110-item extraction taxonomy for legal transcripts
DATE: June 2026 (rebuild session)
STATUS: confirmed

WHAT WAS DECIDED:
Built a list of ~110 specific things that can be extracted from a single court transcript/deposition, grouped into: Case & Matter Intelligence, Attorney Strategy & Judgment, Judge Intelligence, Opposing Counsel Intelligence, Witness Intelligence, Client Intelligence, Fact Pattern Library, and Procedural & Operational Intelligence.

WHY:
Christopher asked for an exhaustive list so the demo would be "incredibly useful and effective, to the point where when I demo it it's immediately obvious the effectiveness." The breadth was a deliberate choice to maximize the value extracted from each transcript, since transcripts are a one-time ingestion cost but the extracted memories compound in value.

ALTERNATIVES CONSIDERED (if known):
A smaller, narrower extraction list — not considered; Christopher explicitly asked for "100 different things or however much it is" rather than a minimal set.

STILL OPEN / NEEDS REVISITING:
This taxonomy is specific to court transcripts/depositions only. It is explicitly flagged as just the first "branch" of a larger planned extraction tree (see "Build a structured roadmap of extraction branches" entry) — different source types (client calls, attorney debriefs, negotiations) will need their own extraction taxonomies, not yet built.

---

### DECISION: No approval queue for extracted memories; use confidence tiering instead
DATE: June 2026 (rebuild session)
STATUS: confirmed

WHAT WAS DECIDED:
Rejected building a human-in-the-loop approval step where a partner reviews/approves each extracted memory before it's stored. Instead, memories are auto-stored with a confidence level (verified/probable/uncertain), and retrieval scoring weights confidence so higher-confidence memories surface more prominently.

WHY:
Christopher's stated reasoning: an approval queue "would make the system clunky" and the priority should be making extraction itself "extremely high quality" rather than adding friction. Claude's supporting reasoning: factual/objective memories (case names, dates, rulings) are low-risk and easy to verify, so they can be auto-stored; interpretive/judgmental memories (judge sympathies, witness credibility) carry more risk of being wrong, but tiering by confidence — rather than blocking storage — lets the system self-regulate, since retrieval already weights verified memories higher than probable ones.

ALTERNATIVES CONSIDERED (if known):
A full approval queue/pending-review workflow before any memory is stored — explicitly proposed by Claude, then explicitly rejected by Christopher in favor of confidence tiering.

STILL OPEN / NEEDS REVISITING:
The "confidence auto-upgrade as patterns repeat across multiple transcripts" mechanism (e.g., a single observation starts as low-confidence, and repeated corroboration across transcripts should raise it) was discussed conceptually but is **not yet implemented in code** — it is on the roadmap, not built.

---

### DECISION: Use a higher-powered model for ingestion/extraction than for querying
DATE: June 2026 (rebuild session)
STATUS: confirmed (decision confirmed; actual model swap to Opus NOT yet implemented in code — currently both ingestion_model and model are set to claude-sonnet-4-6 in config.json)

WHAT WAS DECIDED:
Ingestion (extraction of memories from transcripts) should eventually use a stronger/more expensive model (e.g., Opus) than ordinary query-time responses (Sonnet), because ingestion happens once per document while query cost is ongoing.

WHY:
Christopher's reasoning, stated directly: "all ingestion should be handled by a high power LLM. it would be more money up front but it would make the more human interpretations accurate." Claude's supporting reasoning: ingestion cost is a one-time, front-loaded cost per document, while the resulting memories are queried many times afterward at lower (Sonnet) cost — so paying more for higher-quality extraction is justified given a single case can be worth hundreds of thousands of dollars in fees, and better extraction quality compounds in value over every future query against those memories.

ALTERNATIVES CONSIDERED (if known):
Using the same single model for both ingestion and querying — this was the original/default setup; Christopher explicitly decided to diverge from it, but agreed to keep both set to Sonnet during active development to limit cost/complexity while building, with the explicit caveat that "when we begin uploading a lot of data and building an actual demo we will appropriately use proper models."

STILL OPEN / NEEDS REVISITING:
The actual swap of `ingestion_model` to a stronger model (e.g., Opus) has not yet been done in config.json — both fields are still set to claude-sonnet-4-6 as of the most recent file state. This is an explicitly deferred action item, not a forgotten one. (See also Phase 3 entry "Defer model routing.")

---

### DECISION: Add separate `ingestion_model` and `query_model` fields to config and extractor
DATE: June 2026 (rebuild session, shortly after the above decision)
STATUS: confirmed

WHAT WAS DECIDED:
`config.json` was given separate `model`, `ingestion_model`, and `query_model` keys. `Extractor.__init__` was updated to accept an optional `ingestion_model` parameter (falling back to `model` if not provided), and the extraction API call was switched to use `self.ingestion_model` instead of `self.model`.

WHY:
Direct mechanical implementation of the "different model for ingestion vs. querying" decision above — needed a config-level seam so that swapping ingestion to a different model later (e.g., Opus) requires only a config edit, not a code change.

ALTERNATIVES CONSIDERED (if known):
Hardcoding the model name inside the extractor — rejected implicitly in favor of config-driven model selection, consistent with the rest of the system's config-driven design.

STILL OPEN / NEEDS REVISITING:
None on the mechanism itself. (The actual value swap is still pending — see prior entry.)

---

### DECISION: Court proceedings only — no jury trials, civil cases only, three judges with distinct fictional personas
DATE: June 16 2026 (mid-session, while planning the demo case portfolio)
STATUS: confirmed

WHAT WAS DECIDED:
All fictional demo cases are bench proceedings (depositions, motion hearings, bench trials) in civil court only — no jury trials, no criminal cases. Three fictional judges were created (Hon. Marcus T. Caldwell — Fulton County GA, medical malpractice/personal injury; Hon. Patricia A. Reynolds — Davidson County TN, contract/commercial; Hon. Robert D. Kimball — Cook County IL, employment/professional liability), each with a distinct, internally consistent temperament and ruling pattern.

WHY:
Christopher's reasoning, stated directly: jury reactions are "much harder to predict and write" realistically than a judge's documented rulings, so sticking to bench proceedings keeps the fictional data internally consistent and the judge's behavior is the entire decision-making variable, which is exactly what the product needs to demonstrate pattern recognition. Claude's supporting research, confirmed in conversation: judges are generally assigned by civil/criminal/family/probate division (especially at the state court level), so three judges in three different civil sub-specialties is realistic.

ALTERNATIVES CONSIDERED (if known):
Including jury trial transcripts — explicitly rejected by Christopher for the predictability/writability reason above. Mixing in criminal cases — implicitly rejected in favor of staying within "civil/commercial courts only."

STILL OPEN / NEEDS REVISITING:
None on the civil/bench-only constraint. (Note: as of the last session, only the three Caldwell cases were actually written and loaded; Reynolds and Kimball cases were planned/outlined but not yet written or ingested.)

---

### DECISION: Build a structured roadmap of "extraction branches" (law firm source types + AI agent source types) as a future architecture, not built now
DATE: June 16 2026 (mid-session, while discussing audio ingestion and non-transcript sources)
STATUS: confirmed (as a roadmap item — not implemented in code)

WHAT WAS DECIDED:
Defined two parallel sets of future "extraction branches," each requiring its own dedicated extraction prompt: 8 law-firm-facing branches (court transcripts [built], client calls/meetings, attorney debriefs, settlement negotiations, case documents/filings, court filings, research/precedent, business/operational) and 8 AI-agent-facing branches (web/public record intelligence, document processing, communication monitoring, calendar/deadline intelligence, financial intelligence, relationship intelligence, market/competitive intelligence, real-time proceeding agent). Long-term, an auto-classifier would sit on top of this tree and automatically route any input to the correct branch.

WHY:
Christopher observed that the current 110-item extraction taxonomy is built specifically for court transcripts and would not correctly capture what matters in a client phone call (emotional state, risk tolerance, financial pressure) or an attorney debrief (gut instincts, off-record judge observations) — different source types contain fundamentally different kinds of intelligence, so a single one-size-fits-all extractor is insufficient long-term. Christopher explicitly framed this as a branching-tree architecture: "designing what is effectively a tree with many branches that uses a different extractor (branch) to set parameters for the LLM... toggled by selecting what type of data you are inputting. In the future we would design something that could automatically decide what type of data was being ingested."

ALTERNATIVES CONSIDERED (if known):
Immediately building out all branches now — explicitly rejected; Christopher's direction was "stay focused on getting the court transcripts working well, then branch out to each different extraction type."

STILL OPEN / NEEDS REVISITING:
This entire branch structure is unbuilt. Only Branch 1 (Court Transcript/Deposition) exists in code. No other extractor branch, no source-type selector UI, and no auto-classifier have been implemented.

---

### DECISION: Locked response structure for LLM query responses (skeleton fixed, body content free)
DATE: June 16 2026 (mid-session, after multiple rounds of formatting feedback)
STATUS: confirmed

WHAT WAS DECIDED:
The LLM's query-time response must follow a fixed skeleton every time: Title → Direct Answer → Pattern 1..N (ordered by confidence level, highest first, no cap on number of patterns) → Strategic Synthesis → Confidence Note (always present, fixed position, confidence level stated in the header itself) → Confidence Caveat (only if deviations exist). Within that skeleton, the LLM has full freedom over how it writes the actual prose — no enforced paragraph-length or sentence-count limits.

WHY:
Went through several iterations based on direct user feedback: (1) initially had no fixed structure — too inconsistent. (2) Added a fixed structure with strict paragraph-length/sentence-count rules — Christopher reported this produced "incredibly wordy" walls of text in some responses ("Test 04") versus a cleaner version ("Test 02"), and the difference was diagnosed by Claude as a *tone* problem, not a structure problem: the AI was writing like a legal memo instead of a verbal partner briefing. (3) Removed the strict length rules and added a single tone instruction ("write like a sharp senior partner giving a verbal briefing... not like someone writing a legal memo") — Christopher confirmed this produced the desired result. Christopher separately and explicitly stated the underlying design principle: "too many limiters may take away from the ai and the benefits of ai" — i.e., lock the skeleton, free the content.

ALTERNATIVES CONSIDERED (if known):
Strict paragraph/sentence-length limits inside each section — tried, explicitly identified as a failure mode (too wordy/dense, "wall of text" feedback), then reverted.

STILL OPEN / NEEDS REVISITING:
None on the principle itself (skeleton-fixed/content-free is treated as settled). The exact tone instruction wording could continue to be refined as more query types are tested across Reynolds/Kimball cases.

---

### DECISION: Memory IDs only ever appear in the Confidence Caveat section, never inline in the main analysis
DATE: June 16 2026 (mid-session, direct user feedback)
STATUS: confirmed

WHAT WAS DECIDED:
The LLM is instructed to never cite memory IDs (e.g., "[mem_105654]") inline within the Direct Answer, Pattern sections, or Strategic Synthesis. IDs are only permitted inside the Confidence Caveat section, where they are actionable (the attorney can look them up in the Memory Browser).

WHY:
Christopher's direct feedback: "It should not show the memory ID in the middle of the lines of output. The actual IDs do not help the reader and just muddle up the reading making it not user friendly. But they are ok to be in the 'confidence caveat' section because that directly calls for them to check it."

ALTERNATIVES CONSIDERED (if known):
Inline citation of memory IDs throughout the response (as ChatGPT had suggested in an outside conversation Christopher referenced) — explicitly tested in an earlier version, explicitly rejected by Christopher as cluttering readability.

STILL OPEN / NEEDS REVISITING:
None.

---

### DECISION: Progressive disclosure layout — Confidence Note always visible, Confidence Caveat/Pattern Evidence/Source Memories behind collapsible dropdowns
DATE: June 16 2026 (mid-session, direct user feedback)
STATUS: confirmed

WHAT WAS DECIDED:
Final dashboard layout for a query response: Intelligence Response (always visible) → Confidence Note (always visible, fixed position, plain styling matching the rest of the page, no colored box) → Confidence Caveat summary (visible only if deviations exist) with two separate nested dropdowns underneath it ("View Confidence Details" for the bullet-point detail, "View Pattern Evidence Details" for the full judge/counsel breakdown with corroborating/deviating memory IDs) → Source Memories section showing only the count metrics by default, with a single "View Source Memories" dropdown containing all full memory cards.

WHY:
Iterative direct feedback from Christopher across several rounds: first asked for the pattern-evidence-with-IDs concept at all, then asked for it to be hidden behind dropdowns rather than shown openly, then specifically asked for the Confidence Note's colored "info box" styling to be removed in favor of plain text matching the rest of the response, then asked for the Confidence Caveat's bullet points to also be in their own separate dropdown distinct from the Pattern Evidence dropdown.

ALTERNATIVES CONSIDERED (if known):
Showing full pattern evidence (judge/counsel breakdowns, IDs) openly below the response with no dropdown — tried first, explicitly rejected as too cluttered. A single combined dropdown for both confidence bullet points and pattern evidence — implicitly rejected in favor of two separate dropdowns per Christopher's explicit request.

STILL OPEN / NEEDS REVISITING:
None — this layout was confirmed working as desired in the most recent screenshots reviewed (Test_06_COS.pdf), other than two specific UI issues logged separately below. (Note: Phase 3 surfaced a related but distinct problem — the Source Memories panel and the pattern_evidence counts shown in this same layout draw from two different memory pools. See Phase 3 entry "Source Memories panel shows threshold-filtered set, not full evidence base.")

---

### DECISION: Two pending UI fixes — "Clear" button on Ingest tab, and live-updating memory/vector counters
DATE: June 16 2026 (flagged during testing, not yet fixed in code)
STATUS: confirmed (as identified bugs/requests; fix NOT yet implemented)

WHAT WAS DECIDED:
Two UI improvements were identified and accepted as needed, but not yet built: (1) a "Clear" button next to "Extract and Store Memories" that resets the Source Name field and the transcript text area; (2) the "Total Memories" and "Vector Index" counters at the top of the dashboard should update automatically immediately after an ingestion completes, rather than only updating after a manual page refresh.

WHY:
Christopher identified both directly during testing — buttons being far from the input box, and counters only updating after a manual page refresh.

ALTERNATIVES CONSIDERED (if known):
Not recorded — straightforward bug-fix/feature requests with no alternative approaches discussed.

STILL OPEN / NEEDS REVISITING:
Yes — both are explicitly unfixed as of the last session and were deferred in favor of finishing transcript loading and the retrieval-clustering rework first.

---

### DECISION: Build "Source Traceability" as a distinct feature from the existing "Source Memories" debugging section
DATE: June 16 2026 (discussed in depth, NOT yet implemented in code)
STATUS: confirmed (as a planned feature; not built)

WHAT WAS DECIDED:
Agreed that "Source Memories" (the existing dropdown showing every memory retrieved for a query, with full metadata) and "Traceability" (a future feature showing exactly which memories support *which specific pattern/statement* in the response) are two different things and both should be kept, not merged. Source Memories = full retrieval audit trail. Traceability = lighter-weight, pattern-level attribution.

WHY:
Christopher asked directly whether Source Memories already did this job. Claude's answer, accepted by Christopher: Source Memories answers "what memories were retrieved overall," while Traceability answers "which memories support this specific statement" — different questions, both valuable.

ALTERNATIVES CONSIDERED (if known):
Replacing Source Memories with Traceability — explicitly considered and rejected. Building Traceability immediately — explicitly deferred in favor of loading more transcripts first.

STILL OPEN / NEEDS REVISITING:
Yes — Traceability is fully unbuilt. (Note: Phase 3's "Source Memories panel shows threshold-filtered set" finding gives this feature a concrete, urgent forcing case it didn't have before.)

---

### DECISION: Defer building Traceability until after Reynolds/Kimball transcripts are loaded
DATE: June 16 2026
STATUS: confirmed

WHAT WAS DECIDED:
Rather than building Traceability immediately, the team agreed to first finish loading the Reynolds and Kimball case transcripts (targeting 150-200 memories across 4-5+ cases) and only then build Traceability on top of that fuller dataset.

WHY:
Claude's recommendation, accepted by Christopher: get the foundation solid first, then build Traceability on a richer memory base so it can be seen working meaningfully across multiple matters. Christopher: "I will follow your lead."

ALTERNATIVES CONSIDERED (if known):
Building Traceability immediately on the existing Caldwell-only dataset — available but not chosen.

STILL OPEN / NEEDS REVISITING:
As of the last session, Reynolds and Kimball transcripts were still being written/loaded, so this deferral is still in effect.

---

### DECISION: Defer model routing (Opus for ingestion / Sonnet for queries / local model option) until closer to commercial release or real demo
DATE: June 16 2026
STATUS: confirmed

WHAT WAS DECIDED:
While the decision to eventually use different models for ingestion vs. querying was made early, the actual swap and the broader "model router" concept was explicitly pushed to a later phase, not built now.

WHY:
Christopher's own framing: keep both models the same during development to limit cost/complexity, then "appropriately use proper models" once uploading real data for an actual demo.

ALTERNATIVES CONSIDERED (if known):
Implementing the model swap to Opus immediately — available but explicitly not chosen.

STILL OPEN / NEEDS REVISITING:
This is an explicitly active, not-yet-actioned item — needs to happen before any real client-facing demo, per Christopher's own stated condition.

---

## PHASE 3 — LIVE WORKING SESSION, JUNE 16–17 2026

---

### DECISION: Replace the hard 8-memory retrieval cap with a relevance-threshold + token-budget system
DATE: June 16 2026 (during the live working session)
STATUS: confirmed

WHAT WAS DECIDED:
Removed the fixed "top 8 memories" cutoff in `SearchEngine.retrieve()`. Replaced it with `apply_threshold_filter()`, which includes any memory scoring at or above a relevance threshold (with per-memory-type thresholds), subject to a token budget safety valve that stops adding memories once the estimated token cost of the included memories exceeds `memory_token_budget`.

WHY:
Christopher asked directly: "should we put a hard limit on the memories at 8? would that not limit the ability to recognize pattern and provide solid advice?" His reasoning: an arbitrary count cap could exclude genuinely relevant memories purely because of an arbitrary cutoff, weakening the system's ability to spot real patterns. Claude's supporting reasoning: a relevance threshold lets the LLM see a complete picture of relevant intelligence while still blocking irrelevant memories — security and cost control come from relevance filtering and a token budget, not an arbitrary count.

ALTERNATIVES CONSIDERED (if known):
Keeping the hard count cap — explicitly rejected. Sending all memories above zero threshold with no cap at all — implicitly rejected in favor of adding the token-budget safety valve.

STILL OPEN / NEEDS REVISITING:
None on the mechanism. (The specific threshold numbers chosen are flagged separately below as unverified/provisional.)

---

### DECISION: Memory type relevance thresholds (50/65/80/85) — origin and status
DATE: Originally set June 16, 2026 session; reasoning recovered June 17, 2026
STATUS: confirmed (recovered from a quoted prior exchange) but the underlying values are themselves explicitly unvalidated

WHAT WAS DECIDED:
Threshold tiers were set so precedent/partner_judgment memories need the lowest relevance score (50) to reach the LLM, matter needs 65, client needs 80, operational needs 85 — replacing the earlier hard 8-memory cap. Global `relevance_threshold` default 60, `minimum_relevance_threshold` 40.

WHY:
Recovered direct quote from the prior session: "Judge intelligence memories get a lower threshold because more of them are likely relevant. Client memories get a high threshold because they should almost never appear in a judge query unless directly related." Core principle: memory types central to the product's value (precedent, partner_judgment) should have a low bar so they aren't missed; memory types more likely to contain narrow/sensitive info (client, operational) should require strong relevance match before inclusion. Explicitly stated at the time: this was a design heuristic/estimate, not based on testing or real query data.

ALTERNATIVES CONSIDERED (if known):
An earlier proposed table used different numbers (judge intelligence 50, attorney strategy 65, matter 75, client 85, operational 90) before being rounded/remapped onto memory_type categories in the actual config.json.

STILL OPEN / NEEDS REVISITING:
Explicitly flagged, twice now, as provisional defaults that need revisiting once Reynolds and Kimball transcripts are loaded and real query volume exists across multiple judges. Not yet revisited.

---

### DECISION: Build deviation/corroboration pattern evidence using structured tag-based context clustering instead of raw entity-name matching
DATE: June 16 2026 (same working session, after observing false contradictions in early Caldwell query results)
STATUS: confirmed

WHAT WAS DECIDED:
Rewrote `build_pattern_evidence()` in `SearchEngine` so that before comparing two memories about the same judge/counsel to decide if one "corroborates" or "deviates" from the other, memories are first clustered by ruling context using their `fact_pattern_tags`. Only memories within the same context cluster can be compared for deviation.

WHY:
Christopher observed that early test queries were flagging "deviating" memories that weren't really contradictions — e.g., a judge sustaining one objection type and overruling a different objection type is normal, not inconsistency. Christopher's explicit direction: fix the underlying logic, not just load more transcripts. He specified tags should be placed during extraction, not via extra LLM calls at retrieval time, "to limit LLM usage as much as possible for security and for cost savings."

ALTERNATIVES CONSIDERED (if known):
Short-term fix of loading more transcripts/judges to dilute false positives — offered by Claude as a stopgap, explicitly not chosen as the primary fix. Using an additional LLM call at retrieval time to classify ruling context — rejected in favor of free tags already generated during extraction.

STILL OPEN / NEEDS REVISITING:
The clustering relies entirely on the structured tags being applied consistently during extraction. Not yet validated against Reynolds/Kimball case data because those transcripts weren't yet written/loaded.

---

### DECISION: Add explicit structured-tagging requirements to the extraction prompt (ruling type, legal basis, proceeding context, strategy type, outcome tags)
DATE: June 16 2026 (same session, implementing the clustering decision above)
STATUS: confirmed

WHAT WAS DECIDED:
The extraction prompt in `ingestion/extractor.py` was rewritten to require specific, fixed-vocabulary tags for judge intelligence and attorney strategy memories, rather than allowing the LLM to generate free-form tags.

WHY:
Free-form tags can't be reliably clustered by code — different phrasings of the same concept wouldn't match in a set intersection. A fixed, exact-string vocabulary lets the retrieval engine's clustering logic do reliable set comparisons with zero ambiguity and zero additional LLM calls.

ALTERNATIVES CONSIDERED (if known):
Continuing to let the LLM generate descriptive free-text tags — rejected, since that was the status quo that produced the clustering problem in the first place.

STILL OPEN / NEEDS REVISITING:
This fixed vocabulary currently covers only objection/ruling/motion patterns relevant to the transcripts written so far. Will likely need expansion as Reynolds (contract dispute) and Kimball (employment) transcripts introduce new ruling types and legal bases.

---

### DECISION: Reduce extraction chunk size from 2500 to 1500 words and increase max_tokens from 4000 to 7000
DATE: June 16 2026 (mid-session, in response to repeated JSON parse errors during ingestion)
STATUS: confirmed

WHAT WAS DECIDED:
`Extractor.chunk_word_limit` was set to 1500 (down from 2500), and `max_tokens` on the extraction API call was set to 7000 (after passing through an intermediate value of 8000, then originally 4000).

WHY:
Long transcripts were causing the model's JSON response to be cut off mid-object before completion, producing a literal parse error confirming the output was truncated. Smaller chunks produce fewer memories per chunk, so JSON output per chunk is shorter and less likely to exceed the token ceiling. Claude's reasoning for keeping a limit at all (rather than removing it, as Christopher asked): the Anthropic API has a hard ceiling (~8192 output tokens), so removing the app-level limit would just hit the API's own hard ceiling with no graceful handling. 7000 was chosen as comfortably under that ceiling.

ALTERNATIVES CONSIDERED (if known):
Keeping chunk size at 2500 / max_tokens at 4000 — abandoned, this caused the bug. Removing the token limit entirely — explicitly proposed by Christopher, rejected by Claude for the hard-API-ceiling reason.

STILL OPEN / NEEDS REVISITING:
These specific numbers were arrived at through trial-and-error against observed failures, not first-principles calculation — haven't been stress-tested against an unusually dense or verbose transcript.

---

### DECISION: Second database reset after partial/broken transcript ingestions
DATE: June 16 2026 (mid-session, after the chunking bug above was identified but before it was fixed)
STATUS: confirmed

WHAT WAS DECIDED:
After several transcripts had been ingested partially or with errors (due to the JSON truncation bug), Christopher and Claude agreed to delete `memories.db` and the `chroma.db` folder again and re-ingest all transcripts cleanly using the corrected chunking/token settings.

WHY:
Claude's stated reasoning: starting clean means every memory comes from a complete, properly ingested transcript, making pattern evidence and confidence calculations more accurate.

ALTERNATIVES CONSIDERED (if known):
Manually identifying and deleting only broken/partial memories — not seriously considered; a full reset was simpler given the small number of transcripts at this stage.

STILL OPEN / NEEDS REVISITING:
None — one-time cleanup action, not an ongoing policy.

---

### DECISION: Source Memories panel shows threshold-filtered set, not full evidence base
DATE: June 17, 2026
STATUS: confirmed (this is a discovered/diagnosed fact about existing code, not a forward-looking choice)

WHAT WAS DECIDED:
Confirmed that the "Source Memories" UI panel and the "corroborating/deviating" counts in pattern_evidence are calculated from two different memory pools — Source Memories shows only what survived `apply_threshold_filter()` (score + token budget gated) for one query, while pattern_evidence's corroborating/deviating counts are calculated from `memory_db.get_all_active()` across the entire database, regardless of token budget.

WHY:
Traced directly in the code: `build_pattern_evidence()` in `search_engine.py` calls `get_all_active()` independently of the `top_memories` list used for Source Memories. Confirmed by inspecting both functions side by side, not inferred.

ALTERNATIVES CONSIDERED (if known):
Considered making corroborating count match only what's shown in Source Memories. Rejected — this would make confidence reflect an arbitrary token-budget cutoff rather than actual evidence volume, making confidence LESS accurate, not more.

STILL OPEN / NEEDS REVISITING:
Fix not yet built. Planned approach: keep full-database confidence calculation as source of truth (it's correct), and instead expand Source Memories / add a traceability view so the corroborating/deviating IDs behind a confidence score are inspectable. This is the "source traceability layer" already on the roadmap — this conversation gives it a concrete forcing case (Caldwell query: 39 corroborating cited, only 13 memories visible/auditable).

---

### DECISION: Use a separate decision_log.md instead of relying solely on handoff packets
DATE: June 17, 2026
STATUS: confirmed

WHAT WAS DECIDED:
Created a standalone, append-only decision_log.md, separate from the architecture/handoff packet and roadmap, specifically to capture WHY decisions were made — to be uploaded into the Claude Project's knowledge base so future conversations can read it without manual re-pasting.

WHY:
Directly motivated by hitting a real gap in this conversation: the threshold numbers existed in config.json with no recorded reasoning, forcing reconstruction by inference. Christopher stated the core problem directly: "having to retrain each claude conversation... taking away from the effectiveness of the build." Decision log addresses persistence of reasoning specifically, since handoff packets had been capturing final state but not the reasoning behind decisions made along the way.

ALTERNATIVES CONSIDERED (if known):
Considered letting each old conversation update a single growing copy of the log directly. Rejected — risk of compounding errors/drift across hops, since each instance would be reasoning from both its own session material and an already-assembled document it didn't produce. Settled instead on: blank template + isolated source material per conversation, manual human assembly into the one true master file.

STILL OPEN / NEEDS REVISITING:
None on the mechanism itself. This document is the result of that decision being executed — old conversations' handoff packets and this conversation's own entries have now been merged into one file.

---

### DECISION: Recognize the decision-log/persistence problem as direct validation of the product thesis ("dogfooding" insight)
DATE: June 17, 2026
STATUS: confirmed

WHAT WAS DECIDED:
Recorded as a deliberate observation, not just a passing comment: the exact problem that forced Christopher to build a manual decision_log.md (generic AI memory being too blunt to reliably persist precise, structured, high-stakes reasoning like "why is this threshold 50 and not 55") is structurally the same problem Cognitive OS is built to solve for a law firm at a larger scale. This is being kept as a noted, citable insight for pitch/investor material, not merely a private workflow fix.

WHY:
Christopher connected the two directly: building this project surfaced, firsthand and under real pressure, the same need his own product addresses — persistent, structured, auditable institutional memory that generic AI memory doesn't reliably provide. Claude's refinement of the insight: the manual decision log is the product's underlying philosophy (structured schema, explicit WHY capture, status tagging of confirmed vs. inferred, append-only chronological record) proven out at toy/manual scale — it is not the product itself, since it lacks semantic retrieval, automatic extraction from raw source material, and confidence-weighted relevance scoring. The distinction matters: the value of the insight is "I personally re-derived my own product's core thesis by hitting the same real problem it solves," which is a stronger and more honest claim than implying the manual log proves the full product works.

ALTERNATIVES CONSIDERED (if known):
Treating this as a one-off conversational aside not worth recording — rejected; Christopher explicitly asked for it to be captured in the context document as relevant, specifically for its use as a "we hit the real problem ourselves and solved it the same way our product solves it for clients" validation story.

STILL OPEN / NEEDS REVISITING:
This is a narrative/validation insight, not a technical decision — consider whether it belongs in pitch material (e.g. an investor narrative doc) in addition to this decision log, since its primary value is persuasive/credibility-building rather than architectural.

---

### DECISION: Ran a focused pre-scaling code audit of search_engine.py and structurer.py
DATE: June 17, 2026
STATUS: confirmed

WHAT WAS DECIDED:
Before writing/ingesting ~30 new transcripts, ran a targeted audit of the two most load-bearing files (retrieval scoring/clustering, and structurer validation) rather than an open-ended whole-project review. Surfaced five findings, ranked by relevance to scaling.

WHY:
A bug in scoring/clustering/validation gets baked into hundreds of memories once data is scaled, and is far harder to untangle later than now. An open-ended "read everything" pass was rejected as lower-value because the real bugs this session were found through actual use, not cold reads, and a broad pass would mostly re-derive what's already logged. The audit was scoped to where new data applies the most pressure.

THE FIVE FINDINGS:
1. fact_pattern_tags never validated against controlled vocabulary — typos/drift silently fail to cluster. (FIXED this session.)
2. Judge/counsel names not normalized — formatting differences fragment the evidence base. (FIXED this session, formatting only.)
3. get_ruling_direction() labels rulings favorable/unfavorable from a fixed perspective — a judge ruling consistently for different parties reads as a false deviation. (To be fixed at the data layer via a posture/side tag added during Reynolds extraction design, before ingestion.)
4. retrieval_count creates a rich-get-richer scoring loop that compounds with query volume (i.e., during demos). (Deferred to post-load tuning.)
5. Keyword/targeted memories get a fabricated semantic score via synthetic distance values, inflating them. (Deferred to post-load tuning.)

ALTERNATIVES CONSIDERED:
Open-ended full-project audit — rejected (lower value, would re-derive logged items). Fixing #3 as a blind search_engine patch now — rejected, because a correct fix needs posture/side data that must exist before ingestion.

STILL OPEN / NEEDS REVISITING:
#3 must be addressed in the Reynolds extraction design (posture tag) before any ingestion. #4 and #5 wait for the post-load threshold-tuning pass when real multi-judge query volume exists.

---

### DECISION: Fixed tag drift (#1) and name fragmentation (#2) in structurer.py
DATE: June 17, 2026
STATUS: confirmed (verified working via standalone test script — all 4 test cases passed)

WHAT WAS DECIDED:
Added fact_pattern_tag normalization (lowercase/trim/standardize separators) plus a controlled-vocabulary warning that prints during ingestion for clustering-relevant categories, and added entity-name (judge/counsel/attorney) whitespace normalization — all inside structurer.validate().

WHY:
Clustering/deviation detection depends entirely on fact_pattern_tags matching the fixed vocabulary, but nothing enforced it — drift silently failed to cluster. Names in inconsistent formats fragment the pattern-evidence base. Fixed before scaling so problems aren't baked into hundreds of memories.

IMPORTANT CAVEATS (the code is not a complete fix on its own):
- The controlled tag vocabulary now lives in BOTH structurer.py and search_engine.py. Any new tag must be added to BOTH files or validation and clustering will disagree.
- #1 auto-fixes formatting drift but only WARNS on unrecognized tags ([TAG WARNING] during ingestion) — it does not auto-correct typos. Requires watching console output during ingestion.
- #2 auto-fixes whitespace only. The honorific/length problem ("Hon. Marcus T. Caldwell" vs "Caldwell") cannot be safely auto-merged — canonical naming discipline in transcripts is still required.

ALTERNATIVES CONSIDERED:
Dropping unrecognized tags — rejected (descriptive tags are legitimate for non-clustering categories). Auto-correcting typos — rejected as unsafe guessing.

STILL OPEN / NEEDS REVISITING:
The vocabulary duplication across two files is a known maintenance hazard — a future refactor could move it to a single shared module imported by both.

---

### DECISION: Fixed ChromaDB multi-condition filter bug in vector_db.py (semantic search had been silently failing)
DATE: June 17, 2026
STATUS: confirmed (verified — "Search error... Stopping" gone, scores rose, semantic search now contributing)

WHAT WAS DECIDED:
Rewrote the where-clause construction in search() and search_by_fact_pattern() to wrap multiple conditions in an explicit $and operator (via a _build_where helper), instead of passing multiple top-level keys.

WHY:
The installed ChromaDB version rejects multiple top-level filter keys ("Expected where to have exactly one operator"). This had been causing semantic search to error out and return an empty list on EVERY query — meaning all prior Caldwell results were produced by keyword + targeted search alone, with semantic search contributing nothing. The bug was invisible because keyword/targeted carried the load and still returned plausible-looking results.

CONSEQUENCE WORTH NOTING:
After the fix, results shifted (Caldwell went from 39 corroborating/1 deviation to 41/2, and top scores rose to ~147) because semantic search is genuinely participating for the first time. This is correct behavior, not a regression — but it means any screenshots/results from before this fix were running on a degraded retrieval path and should not be treated as a baseline.

ALTERNATIVES CONSIDERED:
None — straightforward correctness fix.

STILL OPEN / NEEDS REVISITING:
None on the fix itself.

---

### DECISION: Cleaned up loose fix_*/test_* scripts into an _archive_scripts folder
DATE: June 17, 2026
STATUS: confirmed

WHAT WAS DECIDED:
Moved (not deleted) main.py and the loose one-off scripts (fix_congig, fix_dashboard, fix_extractor, fix_identity, test_extract, test_extractor) into an _archive_scripts folder. Confirmed via app.py's import list that none of these are imported by the running app.

WHY:
These were one-time debugging/patch scripts left in the project root after their changes were folded into the real files; they're dead weight relative to the live app. Confirmed safe by checking that app.py only imports from storage/, ingestion/, retrieval/, llm_interface/. Moving (not deleting) preserves them on disk in case any turn out to matter. config.json was explicitly left in place — it is loaded by app.py and is required to run.

ALTERNATIVES CONSIDERED:
Deleting outright — rejected in favor of moving, for safety.

STILL OPEN / NEEDS REVISITING:
The old main.cpython-314.pyc / CognitiveOS class confirms main.py is from a pre-dashboard architecture and is not the current entry point (app.py via "streamlit run dashboard\app.py" is).

---

### DECISION: Reynolds judge + attorney cast design (deliberate contrast, new recurring attorneys)
DATE: June 17, 2026
STATUS: confirmed (design agreed; transcripts not yet written)

WHAT WAS DECIDED:
Judge Patricia A. Reynolds (Davidson County TN, contract/commercial) will be built as a deliberate temperament CONTRAST to Caldwell: discretion-driven, weighs actual prejudice case-by-case (vs Caldwell's bright-line rules), tolerant of procedural informality but intolerant of bad-faith/discovery gamesmanship, allows oral argument to expand beyond the briefs, skeptical of boilerplate damages methodology. Her docket gets a NEW cast of ~5 recurring fixed attorneys (not reusing Caldwell's DeLuca/Tate), each appearing in multiple cases. Target: ~10 transcripts per judge, ~5 recurring attorneys per judge (each in roughly 2-4 cases), ~15 total recurring attorneys across all three judges.

WHY:
Deliberate contrast is a stronger test of the engine — it proves the system tracks PER-JUDGE patterns rather than a generic "judges do X" prior, and stress-tests threshold/clustering against a genuinely different ruling style. New (not reused) attorneys test whether the system keeps per-attorney patterns isolated rather than blurring them. Each attorney must recur across multiple cases because confidence is built from corroborating-vs-deviating counts — a one-off attorney can't form a demoable pattern (matching DeLuca at 14, Tate at 11). Enough attorneys to stress isolation, few enough to stay searchable in a demo.

ALTERNATIVES CONSIDERED:
Reynolds as a slight variation on Caldwell — rejected (weak test; a skeptic could say all the judges look alike). 10 unique one-off attorneys — rejected (impressive volume but produces no usable per-attorney intelligence).

STILL OPEN / NEEDS REVISITING:
Reynolds and Kimball transcripts not yet written. Attorney rosters kept fully separate per judge for now (see cross-judge decision below).

---

### DECISION: Defer cross-judge attorney tracking as a later controlled experiment; sequence complexity one variable at a time
DATE: June 17, 2026
STATUS: confirmed

WHAT WAS DECIDED:
For the initial ~30 transcripts, each attorney appears in front of only ONE judge (rosters fully separate). Cross-judge attorney appearances (testing "how does this attorney perform differently in front of different judges") will be introduced later as a single deliberate controlled test case, after Reynolds is fully validated.

WHY:
build_pattern_evidence() clusters by ruling context but NOT by which judge is on the bench. If one attorney used the same tactic in front of two judges with opposite results (a sensible judge-dependent difference), the current code would likely flag it as a false deviation — the same false-contradiction bug already fixed for one judge, reintroduced one level up. Building cross-judge data now would introduce an untested failure mode at the same time as a brand-new judge persona AND still-unvalidated thresholds, making any odd result impossible to diagnose. Staging complexity one variable at a time keeps each new piece validatable before the next stacks on it.

ALTERNATIVES CONSIDERED:
Building cross-judge attorneys into the initial dataset — rejected (introduces untested clustering gap + confounds diagnosis). Doing everything at once — rejected for the same reason.

STILL OPEN / NEEDS REVISITING:
After Reynolds is ingested and her Pattern Evidence looks sane and clearly distinct from Caldwell's, introduce ONE cross-judge attorney as a controlled test, and use that result to decide whether get_context_cluster() must include judge identity in the cluster key before cross-judge tracking is safe to build out.

---

## PHASE 4 — REPOSITORY, DOCUMENTATION, AND ROADMAP INFRASTRUCTURE (August 22, 2026)

### DECISION: Publish the codebase to a public GitHub repository, scoped as a technical portfolio piece
DATE: August 22, 2026
STATUS: confirmed

WHAT WAS DECIDED:
Created `github.com/ChristopherDudleyAI/cognitive-os` as a **public** repository. `config.json` (live API key) and `data/` (databases) were added to `.gitignore` before the first commit and have never been committed. Business strategy — competitive positioning, go-to-market thesis, the physical-SSD deployment model — is deliberately excluded from everything in the repo.

WHY:
Christopher's stated reasoning: "I want my github profile to ultimately be a showcase of my skills and journey so in the future when i look for a job or anything like that it is something i can show to a potential investor or interviewer." When the strategic content of the decision log was raised as a reason to consider a private repo, he chose instead to keep the repo public and **remove the strategy** from it: "we can remove the stuff about the go to market and competitive strategy and anything else that is not about the technical or development side of the app."

ALTERNATIVES CONSIDERED (if known):
Private repository — offered specifically because the decision log contains competitive positioning against named competitors and unreleased product architecture. Rejected in favor of a public repo with strategy excluded, because the portfolio value depends on it being visible.

STILL OPEN / NEEDS REVISITING:
The decision log itself is gitignored rather than published, so it has no GitHub backup. A separate private repository for it would solve that; not yet set up.

---

### DECISION: Third database reset — clear all ingested data before schema and branch work
DATE: August 22, 2026
STATUS: confirmed

WHAT WAS DECIDED:
Deleted `data/memories.db` and `data/chroma.db` entirely. Code untouched. Christopher's framing: "like a factory reset on a cell phone... only removing uploaded data but leaving the coded structure the same."

WHY:
The database held only Caldwell-era test memories; Reynolds and Kimball transcripts were never written or ingested. With schema changes now planned (`source_type`, `source`, `matter_id`), any memory ingested before those columns exist would need re-ingestion anyway. Clearing before rather than after avoids accumulating records that cannot be threaded or labeled retroactively.

ALTERNATIVES CONSIDERED (if known):
Keeping the Caldwell data and migrating it — not seriously considered; the dataset was small and synthetic, and it predates the schema changes that make it useful.

STILL OPEN / NEEDS REVISITING:
None. This is the third reset (see the two Phase 2/3 entries); the pattern suggests schema should be settled before the next significant ingestion.

---

### DECISION: Cancel the bare_query / Compare mode feature outright
DATE: August 22, 2026
STATUS: confirmed — **supersedes** the Phase 1 entry "Bare-query (no-memory-context) comparison feature exists only for demo purposes and must be removed before commercial release"

WHAT WAS DECIDED:
The "with memory vs. without memory" comparison demo is cancelled, not deferred. Christopher: "i no longer really want to do the bare query / compare mode."

WHY:
Stated as a change of preference, not a technical constraint. Worth recording separately: the prior entry described `bare_query` as an existing method in `llm_interface/interface.py` flagged for later removal. **It does not exist in the code and appears never to have been implemented** — the file was read in full during this session and contains no such method, and the dashboard has no Compare tab. The prior entry therefore recorded a planned feature as though it were built. Christopher confirmed the code files are the most current version he has, so the log was ahead of reality rather than the code being behind.

ALTERNATIVES CONSIDERED (if known):
Building it for demo purposes — previously the plan, now dropped.

STILL OPEN / NEEDS REVISITING:
None. Recorded in `docs/ARCHITECTURE.md` under "Features that were planned but deliberately dropped" so it does not get built by a future session reading the older entry.

---

### DECISION: Track the roadmap in GitHub Issues; add ARCHITECTURE.md for durable constraints
DATE: August 22, 2026
STATUS: confirmed — implemented this session (15 issues created, `docs/ARCHITECTURE.md` written)

WHAT WAS DECIDED:
A three-layer split for project information: **GitHub Issues** for discrete work items (the roadmap), **`docs/ARCHITECTURE.md`** for durable design constraints that shape future work, and **this decision log** for why decisions were made.

WHY:
Christopher's stated problem: "i go long periods of time between sessions and do not want to lose anything." Issues were chosen over a prose roadmap document for four reasons argued in conversation and accepted: they require no manual assembly; open/closed state maintains itself rather than being hand-edited; a merged PR referencing an issue closes it automatically, so "what's still open" stays accurate as a by-product of doing the work; and each issue is sized for a fresh session to pick up cold. The separate ARCHITECTURE.md exists because constraints and tasks are different things — "add a `source_type` column" is a task that closes, while "`source_type` and `extraction_category` are different axes" is a rule that must be readable *before* work starts and never closes.

ALTERNATIVES CONSIDERED (if known):
A single prose `ROADMAP.md` — rejected because it does not track state, does not link to PRs, and reproduces the manual-maintenance problem that caused the drift this decision exists to fix.

STILL OPEN / NEEDS REVISITING:
Every issue must be written self-contained — file paths, what is broken, what the fix looks like — or the mechanism fails the same way prose did. This is a discipline cost with no automated enforcement.

---

### DECISION: Decision log moves into the project folder and is maintained continuously by the AI, not batched by hand
DATE: August 22, 2026
STATUS: confirmed — **supersedes** the June 17, 2026 entry "Use a separate decision_log.md instead of relying solely on handoff packets" (mechanism only; the rationale for having the log at all still stands)

WHAT WAS DECIDED:
The master log moves from `Downloads/decision_log_1.md` to `C:\cognitive_os\decision_log.md`, gitignored. The AI now has write access and appends entries **during** the session as decisions are made. Christopher: "that file does not need to be hand maintained. you can update it."

WHY:
The previous process — AI drafts entries at end of session, Christopher pastes them into a master file — failed in two observable ways, both found this session rather than predicted:
1. **Drift.** The log listed audit finding #3 (ruling posture) as still open. The fix is implemented in both `structurer.py` and `search_engine.py`, with comments explicitly saying "Fixes audit finding #3." The log was behind the code by an unknown number of sessions.
2. **Copy proliferation.** Four decision-log files were found in `Downloads/` — 16, 24, 43, and 50 entries respectively — with no indication of which was authoritative. `decision_log_1.md` was verified as the true master (newest, most entries, and a superset of all three others; the two entries that appeared unique to another copy were confirmed to be title variants of entries already present).

The batching rule was itself the cause: it required the writing to happen at the exact moment context was most exhausted. Christopher had already identified the underlying issue in the June 17 entry — "having to retrain each claude conversation... taking away from the effectiveness of the build" — but the fix at that time addressed persistence of *content* while leaving the *capture mechanism* manual.

ALTERNATIVES CONSIDERED (if known):
Reconstructing the log from the pastes in this conversation — explicitly rejected as unsafe: the two pastes overlapped, and reconstruction risked introducing transcription errors or dropping entries into a permanent append-only record. The filesystem was searched for the real file instead.

STILL OPEN / NEEDS REVISITING:
The three stale copies remain in `Downloads/` and were deliberately not deleted without asking. They should be removed or archived so a future session cannot mistake one for the master.

---

### DECISION: Drop client-call audio from the roadmap; attorney debriefs are the highest-value next source
DATE: August 22, 2026
STATUS: confirmed (direction); no branch built

WHAT WAS DECIDED:
Ingesting recorded incoming client calls is dropped. Christopher: "ok we dont do the customer audio." Attorney debriefs — short dictated notes recorded immediately after a hearing, deposition, or negotiation — are identified as the highest-value next extraction branch.

WHY:
Christopher's original goal was to ingest "every process and communication that a law firm goes through," starting with client audio. Four arguments against audio-first were raised and accepted:
1. **Consent law.** Roughly a dozen US states require all-party consent to record — including Illinois, where the Kimball cases are set. Recording an intake call without consent in those states is a crime, making consent capture a product requirement rather than polish.
2. **Privilege.** Sending recorded privileged client communication to a third-party API is exactly the exposure that pushes firms toward local models; the ABA issued a formal opinion on generative AI and client confidentiality in 2024.
3. **Speaker attribution.** "The client said X" and "the attorney advised X" are different memories and one may be privileged advice. Diarization on a poor phone line is unreliable, and a mislabeled speaker creates a false memory that permanently pollutes pattern evidence.
4. **Cost-to-value.** Transcription itself is a commodity; the expensive parts are consent infrastructure and attribution, and the payoff is lower than cheaper text sources.

Attorney debriefs were argued as the inverse on every axis: highest judgment density per token in the firm (they record *why*, which nothing else captures), no consent burden (the attorney is talking to themselves), short enough to be cheap to ingest, and they capture precisely the tacit knowledge that leaves when a partner retires. Christopher: "i never thought about attorney debriefs."

ALTERNATIVES CONSIDERED (if known):
Client-call audio as branch two — dropped. Email was assessed as a strong candidate but sequenced after debriefs: already text, already threaded and attributed, but high-volume and low signal density, which will stress the untuned retrieval thresholds.

STILL OPEN / NEEDS REVISITING:
A full source-value ranking (twelve sources, high to low) was produced in conversation and is not yet written into any document. Worth capturing before it is lost — it is not in the repo, this log, or an issue.

---

### DECISION: Capture source_type, matter_id, source, and date_of_event at ingest rather than inferring them
DATE: August 22, 2026
STATUS: confirmed (design); not implemented — GitHub issue open

WHAT WAS DECIDED:
The Ingest tab becomes a form collecting four fields the model cannot supply: `source_type` (dropdown, selects the extraction branch), `matter_id`, `source`, and `date_of_event`.

WHY:
Christopher proposed the dropdown: "above the ingestion text box there would be a drop down where you can select what kind of information you are uploading... that way it would also allow the extraction prompts to be much more focused and streamlined." Note this independently re-derives his own June 16 entry, which described the same toggle. The scope was then widened in conversation on the argument that the dropdown is not a prompt selector but the first field of a labeling form — an LLM cannot know a firm's matter numbering, cannot know whether a document is the third or thirtieth in a case, and often cannot date an event from its text. All four fields are far cheaper to capture at the door than to reconstruct, and `matter_id` in particular cannot be retrofitted without full re-ingestion.

ALTERNATIVES CONSIDERED (if known):
The dropdown alone, without the other three fields — superseded within the same conversation once the labeling argument was accepted.

STILL OPEN / NEEDS REVISITING:
Depends on the `source_type` and `source` columns existing and `matter_id` being populated. Best implemented alongside the branch architecture rather than before it.

---

### DECISION: source_type is a distinct schema axis from extraction_category
DATE: August 22, 2026
STATUS: confirmed (design); not implemented — GitHub issue open

WHAT WAS DECIDED:
Add `source_type` as its own column. It records where a memory came from; `extraction_category` records what it is about. Do not overload one for the other.

WHY:
The two are genuinely different dimensions and conflating them costs capability. A `judge_intelligence` memory sourced from a written court order is the judge's own stated reasoning; the same category sourced from an attorney debrief is one person's read of a mood. Four concrete uses were argued: retrieval weighting by source reliability, preventing clustering across incompatible source types, per-branch extraction quality auditing, and producing the labeled dataset a future source-type auto-classifier would need to train on.

ALTERNATIVES CONSIDERED (if known):
Encoding source type inside `extraction_category` — rejected; it would make the category vocabulary combinatorial and would break the existing category-based clustering filters.

STILL OPEN / NEEDS REVISITING:
Whether retrieval should weight source types with fixed multipliers or something adaptive is not decided.

---

### DECISION: Extraction branches share a fixed spine; taxonomy, vocabulary, chunking, model, and confidence vary
DATE: August 22, 2026
STATUS: confirmed (design); not implemented — GitHub issue open

WHAT WAS DECIDED:
**Shared across every branch:** the output JSON contract, entity field names (`judge`, `opposing_counsel`, `source_attorney`), `matter_id`, and the core extraction rules. **Varies per branch:** extraction taxonomy, controlled `fact_pattern_tags` vocabulary, chunk size, model selection, and default confidence level.

WHY:
Fully independent per-branch prompts would produce N opportunities for drift and N incompatible outputs. The entity field names are the specific danger: `build_pattern_evidence()` groups memories by those exact keys, so a branch emitting `judge_name` instead of `judge` silently produces no cross-source patterns — no error, no warning. Chunk size and model varying per branch follows from the sources themselves: an email thread and a 200-page transcript do not chunk alike, and dense human judgment warrants a stronger model than mechanical records. The existing `ingestion_model` config seam already supports per-branch model selection; it needs to become per-branch rather than global.

ALTERNATIVES CONSIDERED (if known):
One universal extraction prompt across all source types — rejected in the June 16 entry already, on the grounds that different source types contain fundamentally different intelligence.

STILL OPEN / NEEDS REVISITING:
A written spec for how a branch is *defined* does not exist yet. Without it, adding branch three means re-deriving this design.

---

### DECISION: Confidence defaults are set per branch, not by model self-assessment
DATE: August 22, 2026
STATUS: confirmed (design); not implemented — GitHub issue open

WHAT WAS DECIDED:
Each extraction branch sets a default `confidence`. The extractor may downgrade but not upgrade it.

WHY:
Source type predicts reliability better than a model's self-report. A written court order is `verified` by construction — it is the primary document. An attorney's impression that a judge seemed sympathetic is `uncertain` regardless of how confidently it is phrased. This also fixes a live problem: `confidence` currently defaults to `probable` for essentially everything, and `score_memory()` weights it 20/10/0 — so a scoring dimension that was designed to carry signal currently carries almost none.

ALTERNATIVES CONSIDERED (if known):
Continuing to let the extractor self-assess — the status quo, rejected as both less accurate and effectively inert.

STILL OPEN / NEEDS REVISITING:
Interacts with the unimplemented confidence auto-upgrade mechanism (separate issue). Whether a branch default should be overridable by corroboration is not decided.

---

### DECISION: Vocabulary consolidation is now a prerequisite, not deferred cleanup
DATE: August 22, 2026
STATUS: confirmed — **supersedes** the June 17, 2026 status of the tag-drift fix, which listed vocabulary duplication as "a known maintenance hazard" for "a future refactor"

WHAT WAS DECIDED:
Extracting the controlled tag vocabularies into a single shared module is now a blocker that must be done **before** the second extraction branch is built.

WHY:
The vocabularies (`ruling_type_tags`, `legal_basis_tags`, `proceeding_tags`, `strategy_tags`, `outcome_tags`, `posture_tags`) are defined twice — `structurer.py` lines 13-55 and `search_engine.py` lines 31-82 — and a tag added to one but not the other makes validation and clustering disagree silently. The branch architecture changes the arithmetic: at one branch this is two copies to keep in sync; at eight branches with per-branch vocabularies it is sixteen copies of a failure mode that produces no error and no visible symptom beyond patterns quietly not forming. The original entry correctly identified the hazard but scoped the fix as optional; the branch decision makes it load-bearing.

ALTERNATIVES CONSIDERED (if known):
Continuing to maintain duplicates by discipline — rejected; the failure is silent, so discipline has no feedback signal to correct against.

STILL OPEN / NEEDS REVISITING:
None on the decision. The work is open as a GitHub issue.

---

### DECISION: The pattern-confidence engine is scoped to observed behavior, not cross-lifecycle prediction
DATE: August 22, 2026
STATUS: confirmed as a design constraint; no code change made

WHAT WAS DECIDED:
The corroboration/deviation confidence mechanism is treated as valid for **observed behavioral patterns** ("this judge sustains foundation objections in depositions") and **not** as a basis for cross-lifecycle predictive claims ("clients who present as financially pressured settle for less"). If both are ever rendered in the same confidence UI, they must be visually distinguished.

WHY:
Raised in response to Christopher's stated goal of pattern recognition "from even the individual customers and their initial calls to the final outcome." Behavioral patterns have a tight causal link and directly comparable observations. Lifecycle-outcome claims involve many intervening variables, and a boutique firm generates only a few hundred matters a year — fourteen corroborating observations is strong evidence about a judge's habits and near-meaningless as a predictive claim about client psychology. The risk identified: the existing UI would render both as "HIGH CONFIDENCE" identically, and an attorney could act on a small-sample coincidence presented with the authority of a well-established pattern.

ALTERNATIVES CONSIDERED (if known):
Not recorded — this was raised as an analysis point and accepted rather than debated between options.

STILL OPEN / NEEDS REVISITING:
No mechanism yet distinguishes the two claim types. Becomes urgent only when non-transcript sources are ingested and cross-lifecycle patterns become possible to form. Recorded in `docs/ARCHITECTURE.md` section 9.

---

### DECISION: matter_id is never populated — discovered, not decided
DATE: August 22, 2026
STATUS: confirmed (verified in code this session)

WHAT WAS DECIDED:
Recorded as a discovered fact: `matter_id` is `None` on every memory in the system. The extraction prompt in `extractor.py` never asks the model for it, so `structurer.py:94` (`candidate.get('matter_id', None)`) always resolves to `None`.

WHY:
Found by grepping `extractor.py` for `matter_id` and getting zero matches, while the same grep across `storage/`, `retrieval/`, and `dashboard/` returned the full plumbing: a database column, `MemoryDB.get_by_matter()`, the ChromaDB metadata filter, the `SearchEngine.retrieve()` parameter, and the context-packet field. Every consumer exists; nothing produces the value. Consequence: `get_by_matter()` returns an empty list for any input, and the matter filter never matches. This matters disproportionately because `matter_id` is the thread the entire intake-to-outcome ambition depends on.

ALTERNATIVES CONSIDERED (if known):
Having the extractor infer `matter_id` from document text — rejected; an LLM cannot know a firm's matter numbering scheme.

STILL OPEN / NEEDS REVISITING:
Fix is an open GitHub issue. Must happen before significant ingestion — retrofitting requires re-ingesting everything.

---

### DECISION: source and project are accepted by the structurer and discarded — discovered, not decided
DATE: August 22, 2026
STATUS: confirmed (verified in code this session)

WHAT WAS DECIDED:
Recorded as a discovered fact: the Source Name the dashboard requires is never persisted. `dashboard/app.py:488` collects it and validates it as mandatory, passes it to `structure_batch(candidates, source=source_name)`, which passes it to `structure(candidate, source, project)` — where neither `source` nor `project` is used. There is no `source` field in the memory dict and no column in the database.

WHY:
Found by grepping `structurer.py` for every use of `source`: the only hits are the two function signatures, the pass-through call, and the unrelated `source_attorney` field. Consequence: there is currently no way to tell which document any memory came from, which blocks per-document extraction auditing, removing or re-ingesting a single bad transcript without a full reset, and the planned source traceability layer.

ALTERNATIVES CONSIDERED (if known):
Not applicable — this is a defect, not a choice. Whether `project` is still wanted at all is an open question in the issue.

STILL OPEN / NEEDS REVISITING:
Fix is an open GitHub issue. Adding the column means a migration or another database reset; a reset is acceptable while there is no production data.

---

### CORRECTION: ruling posture fix (audit finding #3) is implemented — the log was stale
DATE: August 22, 2026
STATUS: confirmed (verified in code) — **corrects** the June 17, 2026 entry "Ran a focused pre-scaling code audit of search_engine.py and structurer.py," which lists finding #3 as "To be fixed at the data layer via a posture/side tag added during Reynolds extraction design, before ingestion"

WHAT WAS DECIDED:
Recorded as a correction: the posture-tag fix **is built**. `posture_tags` (`favored_plaintiff`, `favored_defendant`, `favored_neither`) exists in `structurer.py` lines 44-46 and `search_engine.py` lines 78-82, in both cases with a comment reading "Fixes audit finding #3. MUST stay in sync with [the other file]." The extraction prompt in `extractor.py` carries a full RULING POSTURE section instructing the model to determine which party a ruling benefited by effect rather than by verb.

WHY:
Found by reading the source files directly at the start of this session. The log's own rule — "Never let an entry sound more certain than it actually is" — was satisfied at the time it was written; the entry simply predates the work. Christopher's explanation for how this happened: "many times as i coded i had to go back and manually update decision logs because i was using multiple chat lines due to the context being filled so fast." This drift is the direct evidence behind the process change logged above.

ALTERNATIVES CONSIDERED (if known):
Not applicable.

STILL OPEN / NEEDS REVISITING:
Whether the posture tagging actually works as intended is **unverified** — it has never been exercised against ingested data, since the database was reset and Reynolds/Kimball transcripts were never written. The code exists; its correctness is untested.

---

### DECISION: Publish the decision log; keep only secrets out of the repository
DATE: August 22, 2026
STATUS: confirmed — **supersedes** the earlier August 22, 2026 decision to gitignore this file, and narrows the "strategy stays out of the repo" scope in the entry "Publish the codebase to a public GitHub repository, scoped as a technical portfolio piece"

WHAT WAS DECIDED:
`decision_log.md` is committed to the public repository. The exclusion list narrows to secrets and machine-local artifacts only: `config.json` (live API key), `data/` (local databases), `__pycache__/`, `venv/`, and `.claude/settings.local.json`. Christopher: "i dont think i really need to keep anything private aside from security related things like my api keys."

WHY:
Stated as a direct preference. It reverses a concern raised earlier in the same session — that the log contains competitive positioning against named competitors, an unreleased physical-device product model, and go-to-market reasoning, all of which become visible to anyone. Christopher considered that and chose publication anyway. Two things follow that argue in its favor rather than against: the log gains an off-machine backup it did not have while gitignored, which was the original problem being solved; and for the portfolio purpose stated in the repo-creation entry, a documented reasoning trail is arguably a stronger signal to an interviewer than the code alone.

Before publishing, the file was scanned for API-key patterns (`sk-ant-`, `sk-`, `ghp_`, `gho_`, AWS `AKIA`), password and secret assignments, and email addresses. All clean. Case and party names throughout are fictional by design (see the Phase 2 entry on the three fictional judges), so no real client or matter information is exposed.

ALTERNATIVES CONSIDERED (if known):
Keeping it gitignored, or maintaining a redacted technical-only version in the repo alongside a full private copy — both available, neither chosen. Christopher opted for the simpler arrangement of one file, published.

STILL OPEN / NEEDS REVISITING:
If the project later moves toward fundraising or a client-facing commercial phase, whether the competitive-positioning material should still be public is worth re-examining. It is reversible only in the weak sense — the file can be removed going forward, but published git history persists.

---

### CORRECTION: details recovered from a superseded log copy before it was deleted
DATE: August 22, 2026
STATUS: confirmed — **clarifies** two Phase 3 entries: "Memory type relevance thresholds (50/65/80/85) — origin and status" and "Reduce extraction chunk size from 2500 to 1500 words and increase max_tokens from 4000 to 7000"

WHAT WAS DECIDED:
Recorded as recovered detail, not a new decision. Before deleting the three stale decision-log copies from `Downloads/`, each was diffed against the master. `CognitiveOS_Decision_Log.md` (24 entries, June 17 11:42) held two entries whose *titles* differed from the master's but whose *bodies* contained material the master's versions had dropped. Both details are preserved here.

**1. The threshold numbers — the config/conversation mismatch was accidental, not deliberate.**
The master's entry states that an earlier proposed table (judge intelligence 50, attorney strategy 65, matter 75, client 85, operational 90) was "rounded/remapped onto memory_type categories in the actual config.json," which reads as an intentional design step. The superseded copy is explicit that it was not: *"the discrepancy itself was not deliberate, just inconsistent transcription from concept to code."* The values in `config.json` (precedent/partner_judgment 50, matter 65, client 80, operational 85) therefore differ from the reasoning that produced them **by accident**, and no one has since checked whether the transcribed numbers or the originally-reasoned ones are the better choice.

The same entry also preserved a direct acknowledgment that the master paraphrases more softly: *"The thresholds aren't based on testing or data — they were my initial estimate... a design assumption, not a tested conclusion."*

**2. The JSON truncation bug — the literal error text.**
The master says a parse error confirmed truncation. The superseded copy records the actual console message: `"Expecting property name enclosed in double quotes"` at a specific line and column. Useful for recognizing the failure if it recurs.

WHY:
Both details were nearly lost to routine cleanup. The threshold one matters most: it means the live config values are the product of a transcription slip rather than a decision, which is a materially different thing to inherit — and it makes the open threshold-tuning work (GitHub issue) more urgent, since the starting point is not even the number that was reasoned for. This is a concrete instance of the log's own rule that an entry must never sound more certain, or more deliberate, than the thing it describes.

ALTERNATIVES CONSIDERED (if known):
Deleting the stale copies without diffing them, on the basis that the master had more entries — this was the initial plan and would have silently discarded both details. The entry-title comparison flagged two apparent mismatches, and inspecting the bodies rather than assuming they were harmless title variants is what surfaced this.

STILL OPEN / NEEDS REVISITING:
Whether the config's transcribed thresholds or the originally-reasoned ones are correct is unresolved and should be settled during the threshold-tuning pass. All four `Downloads/` copies have now been deleted; the project copy is the only one.

---

### DECISION: Ingest form captures labels; extraction gets a branch-routing seam
DATE: August 22, 2026
STATUS: confirmed — implemented and tested (closes the four labeling issues)

WHAT WAS DECIDED:
Built the labeling batch as one change while the database was empty:
- **Schema:** added `source` and `source_type` columns. Column order now lives once in `MemoryDB.EXPECTED_COLUMNS`; `row_to_dict()` derives from it instead of keeping a second hand-maintained list.
- **Migration:** added `MemoryDB.migrate_schema()`, which `ALTER TABLE`s any missing column on startup.
- **Structurer:** `structure()` and `structure_batch()` now accept and persist `source`, `source_type`, `matter_id`, and `date_of_event`. Form values take precedence over anything the model emits. The unused `project` parameter was removed.
- **Extractor:** added a `BRANCHES` registry keyed by source type, each entry naming a prompt builder, chunk size, and default confidence. `extract()` routes through it and falls back to the court-transcript branch for unknown types. Prompt text is unchanged; it moved into `_court_transcript_prompt()` and the API call moved into `_call_model()`.
- **UI:** Ingest tab now collects Source Type, Source Name, Matter ID, and Date of Event. Source Name, Matter ID, and text are required; the warning names exactly which are missing.
- **Vector store:** `source_type` and `source` added to ChromaDB metadata so semantic search can filter on them later.

WHY:
Sequencing was the whole argument. The database was empty following the third reset, which made schema changes free — no migration, nothing to re-ingest. Any memory ingested before these fields existed would have needed full re-ingestion, since none of the four can be inferred from document text. Doing this before writing transcripts avoids a fourth reset for the same reason as the first three.

Two design choices worth recording:
1. **The dropdown is generated from `Extractor.BRANCHES`, not a config list.** It therefore cannot offer a source type with no extraction prompt behind it — the two cannot drift apart.
2. **The routing seam was built now; the branches were not.** Only the court-transcript branch exists. Adding a second means adding a registry entry and a prompt builder rather than editing the extraction flow. This mirrors the existing `ingestion_model` config seam: build the seam early, fill it later.

Christopher deferred the timing question — "ill let you decide when you think we are at a point to write transcripts" — so the sequencing call (labels before data) was made rather than asked.

ALTERNATIVES CONSIDERED (if known):
Writing Reynolds transcripts first, since it produces visible progress — rejected: anything ingested first would be thrown away. Adding `matter_id` to the extraction prompt — rejected on the standing rule that a model cannot know a firm's matter numbering. Building all eight extraction branches now — out of scope; only the seam was built. Keeping `project` and wiring it up — rejected as speculative; removed instead of left dangling.

STILL OPEN / NEEDS REVISITING:
Per-branch `default_confidence` is declared in the registry but not yet applied — `structurer` still defaults everything to `probable`. That is the separate confidence-defaults issue and needs the second branch to be meaningful.

---

### CORRECTION: schema changes no longer require a database reset
DATE: August 22, 2026
STATUS: confirmed (verified by test against a simulated legacy database)

WHAT WAS DECIDED:
Recorded as a change in what is true, not a new decision: adding a column no longer forces a wipe. Three of this project's database resets were driven at least partly by schema evolution against `CREATE TABLE IF NOT EXISTS`, which silently leaves an existing table at its old shape — so every `save()` afterward fails on column count with no obvious cause.

`MemoryDB.migrate_schema()` now reads `PRAGMA table_info` on startup and `ALTER TABLE`s in any column missing from `EXPECTED_COLUMNS`, printing what it added.

WHY:
Verified rather than assumed: a 23-column database was constructed with a pre-existing row, opened with the new code, and checked. Both columns were added, the existing row survived intact and read back with `None` in the new fields, and a subsequent save with the new columns succeeded.

ALTERNATIVES CONSIDERED (if known):
Continuing to reset the database on schema change — the de facto practice until now; it works only while data is disposable, which stops being true the moment real transcripts are loaded.

STILL OPEN / NEEDS REVISITING:
The migration only adds columns. Renaming, dropping, or changing a column type is not handled and would still need manual intervention.

---

### CORRECTION: audit finding #3 was only half implemented — the posture tags were never read
DATE: August 22, 2026
STATUS: confirmed (demonstrated with a failing case, then fixed and re-tested) — **corrects the August 22, 2026 correction entry** "ruling posture fix (audit finding #3) is implemented — the log was stale"

WHAT WAS DECIDED:
Recorded as a correction to a correction. Earlier today an entry was written stating that the posture-tag fix for audit finding #3 was built, based on finding `posture_tags` defined in both `structurer.py` and `search_engine.py` with comments reading "Fixes audit finding #3." That entry flagged, correctly, that the code had never been exercised against data and its correctness was untested.

Exercising it revealed the fix was **half built**:
- The extraction prompt requires posture tags — built.
- `structurer.py` validates them against the controlled vocabulary — built.
- `search_engine.py` declared `self.posture_tags` — and **never read it anywhere**. `get_ruling_direction()`, the exact function the audit identified, still used its own hardcoded favorable/unfavorable partition of ruling verbs.

The false-contradiction bug the posture tags were created to fix was therefore still live. Demonstrated concretely: a judge who grants the plaintiff's summary-judgment motion in one matter and denies the defendant's in another has ruled *for the plaintiff both times*, but the verb-based logic returned `'favorable'` for the first and `'unfavorable'` for the second, placing them in the same context cluster with opposing directions — counting the judge as deviating from himself.

`get_ruling_direction()` now prefers the posture tag when present and falls back to the verb partition only when it is absent.

WHY:
Found while consolidating the tag vocabulary (the separate decision below). Grepping for tag literals outside the new shared module surfaced the hardcoded favorable/unfavorable sets, and checking what consumed `posture_tags` returned only the assignment line. This is the second time in one session that a feature's plumbing existed with nothing feeding it — the same shape as `matter_id` and `source`.

Worth recording as a pattern: **a declared-but-unread attribute is this project's characteristic failure mode.** It produces no error and no visible symptom, so it survives until something specifically looks for consumers rather than definitions.

ALTERNATIVES CONSIDERED (if known):
Treating an un-postured ruling memory as `'neutral'` (never deviating) rather than keeping the verb fallback — rejected. It would fail toward over-confidence: if posture tagging degraded, deviation detection would go silent and the engine would report high confidence with no dissent, which is the more dangerous direction for an attorney relying on it. The verb fallback returns values from a deliberately different vocabulary (`'favorable'` vs `'favored_plaintiff'`), so an un-postured memory can never compare equal to a postured one; in a mixed cluster that surfaces as a deviation, which lowers confidence rather than inflating it.

`favored_neither` maps to `'neutral'` rather than becoming its own direction, since it marks a procedural ruling with no directional signal and `build_pattern_evidence()` already treats `'neutral'` as non-deviating.

STILL OPEN / NEEDS REVISITING:
Still untested against ingested data — the tests were direct unit-level calls, not a full ingest-and-query cycle. Verify against Reynolds transcripts once written. The mixed-cluster case (some memories postured, some not) is handled safely but has not been observed in practice.

---

### DECISION: Consolidate the controlled tag vocabulary into vocabulary.py
DATE: August 22, 2026
STATUS: confirmed — implemented and tested (closes the vocabulary-consolidation issue)

WHAT WAS DECIDED:
All controlled tag vocabularies now live in a single top-level `vocabulary.py`. `structurer.py` and `search_engine.py` import from it and alias onto instance attributes so existing access keeps working. Purpose-named unions replace the ad-hoc ones that were previously assembled inline at each use site: `CONTROLLED_VOCABULARY` (validation), `CLUSTERING_TAGS` (context clustering), `SCORING_TAGS` (relevance bonus), and `FAVORABLE_/UNFAVORABLE_RULING_TAGS` (the direction fallback).

WHY:
The duplication had already drifted, which was verified rather than assumed before starting:
- **Tag contents matched** across both files for all five shared sets.
- **`OUTCOME_TAGS` existed only in `structurer.py`** — `search_engine.py` had no concept of it.
- **The scoring union omitted both outcome and posture tags.** A memory tagged `strategy_succeeded` or `favored_plaintiff` earned **zero** structured-tag bonus, despite the extraction prompt *requiring* those tags on strategy and ruling memories. `ruling + posture` scored 3 instead of 6.

The June 17 entry correctly identified the duplication as a maintenance hazard and scoped the fix as a future refactor. It had already caused a live scoring bug by then. The branch architecture made it urgent — two copies becomes sixteen at eight branches — but the drift did not wait for that.

Consolidation is enforced by identity, not discipline: both consumers now reference the *same frozenset objects*, verified with an `is` check rather than equality. They cannot drift.

ALTERNATIVES CONSIDERED (if known):
Keeping the duplication and maintaining it by discipline — rejected; the failure is silent, so discipline has no feedback signal to correct against. Consolidating without fixing the scoring gap, to keep the refactor purely behavior-preserving — rejected: the gap was unambiguously unintended, the extraction prompt requires the tags that were being ignored, and leaving a known bug in place while performing the exact refactor that surfaced it would be strange. The change is noted as a behavior change in the pull request.

STILL OPEN / NEEDS REVISITING:
Scores now rise for memories carrying outcome or posture tags, which interacts with the untuned relevance thresholds — and those are themselves a transcription slip rather than a reasoned value. Both should be settled in the same threshold-tuning pass.

---

### DECISION: Demo source material moves into the repository and is versioned
DATE: August 22, 2026
STATUS: confirmed

WHAT WAS DECIDED:
The Character Bible and all demo transcripts now live in the repository — `docs/CHARACTER_BIBLE.md` and `demo_data/<judge>/`. A `demo_data/README.md` records the structure and the three rules that cause the most damage when broken (canonical naming, attorney isolation, honest posture mix).

WHY:
A search of the filesystem turned up the Character Bible and exactly **one** Caldwell transcript, both in `Downloads/`. The bible existed in two copies, though unlike the decision log they were byte-identical. This is the third critical project artifact found living in `Downloads/` in a single session.

The transcript loss is the concrete cost. The decision log records three Caldwell cases written and roughly 101 memories ingested; only `Hayes v. Riverside` survives on disk. The database was reset, so the extracted memories are gone too — meaning two cases' worth of source material no longer exists in any form and would have to be rewritten from scratch, with no way to keep the new versions consistent with what the originals established.

**Unresolved discrepancy, recorded rather than guessed at:** the Character Bible's "Cases already written" section lists **one** Caldwell case; the decision log says **three** were written and loaded. The bible is dated June 17 23:01. Either cases 2 and 3 were written afterward and the bible was never updated, or the log's count was imprecise. The available evidence does not settle it. What is certain is that one transcript exists on disk today.

ALTERNATIVES CONSIDERED (if known):
Leaving demo data out of the repo as disposable test fixtures — rejected on the evidence: it was treated as disposable and two files were lost. Transcripts are not fixtures, they are the source material the demo rests on, and internal consistency across them is the thing that makes the pattern engine demonstrable.

STILL OPEN / NEEDS REVISITING:
Caldwell's docket needs eight or nine more cases and Kimball's needs ten; only Reynolds has moved. Whether to rewrite the two lost Caldwell cases or simply write forward from case 2 is unresolved — nothing depends on reproducing the originals, since the memories are gone either way.

---

### DECISION: Reynolds docket opened with three transcripts
DATE: August 22, 2026
STATUS: confirmed — written and audited, not yet ingested

WHAT WAS DECIDED:
Wrote the first three Reynolds cases, following the Character Bible's specification for her without deviation:
- **Brightwater Logistics v. Sumner Freight** (Discovery Hearing) — Soto v. Kowalski. Establishes the stonewalling trigger and the remedy-matches-harm rule.
- **Ashfield Millwork v. Calloway Development** (Motion Hearing) — Okafor v. Lange. Anti-boilerplate rule applied to **both** parties in the same hearing.
- **Vantage Point Analytics v. Hartwell Capital** (Summary Judgment) — Pace v. Anand. Establishes oral-argument expansion past the briefs, and her disfavor for settlement strong-arming.

WHY:
Timing: everything cheaper to do on an empty database was finished — labels captured at ingest, schema migration in place, vocabulary unified, and the deviation engine actually reading posture tags. Christopher had delegated the timing decision ("ill let you decide when you think we are at a point to write transcripts"), so this was the point.

Reynolds first rather than more Caldwell, because she is the designed contrast: a **conduct** lean rather than a **party** lean. If the engine can learn "this judge favors whoever acted in good faith" as distinct from "this judge favors plaintiffs," that is the strongest available evidence it is detecting real per-judge patterns rather than a generic prior.

The Ashfield case is the deliberate centerpiece: her anti-boilerplate rule strikes the defense's templated Daubert challenge **and** the plaintiff's benchmark-multiplier damages figure, in the same hearing, on the same reasoning. A party-lean judge cannot produce that transcript.

Audited before committing rather than after: attorney isolation verified with word-boundary matching against both other dockets (an initial substring check produced a false "William Tate" leak — it was matching inside "STATE OF TENNESSEE"), canonical judge name present in all three, and posture mix hand-classified by effect at 6 plaintiff / 5 defendant / 1 neither, against the bible's ~45/45/10 target.

ALTERNATIVES CONSIDERED (if known):
Writing all ten Reynolds cases at once — rejected; three establishes the pattern and can be ingested and checked before committing to the shape. Starting with Kimball — rejected; Reynolds is the sharper contrast to the docket that already exists.

STILL OPEN / NEEDS REVISITING:
**Not yet ingested.** These have never been run through extraction, so the tag vocabulary landing cleanly, the posture tags being applied correctly by effect rather than verb, and the deviation engine reading them as intended are all still unverified against real data. That run is the first genuine end-to-end test of everything built today.

Two of the five Reynolds defense counsel are unused so far — Helena Cross and Gregory Whitfield. The bible wants each in 2–4 cases, so they need to feature in the next batch, and Kowalski, Lange, and Anand each need at least one more appearance.

---

### DECISION: First end-to-end ingestion run — what it verified and what it broke
DATE: August 22, 2026
STATUS: confirmed (measured against real ingested data)

WHAT WAS DECIDED:
Recorded as findings from the first genuine end-to-end run. Three Reynolds transcripts ingested, 62 memories stored, one query executed. Four API calls, roughly $0.23 at Sonnet list pricing. Christopher authorized key usage with a standing condition of asking before each use.

**Verified working — all previously untested against real data:**
- All four ingest labels populated on 62/62 memories. `get_by_matter()` returns 22 / 21 / 19 for the three matters. The labeling work is confirmed beyond the unit test.
- Canonical judge name on 62/62 (`Patricia A. Reynolds`), so the name-normalization rule holds under real extraction.
- 204 of 206 `fact_pattern_tags` inside the controlled vocabulary. The two outliers (`contract_dispute`, `routing_obligations`) sat on non-clustering categories, so the drift warning correctly stayed silent.
- Pattern evidence assembled: Reynolds MEDIUM (26 corroborating / 9 deviating), plus three opposing-counsel profiles.

**Broken, and the reason matters more than the count:**

1. **Posture coverage is only 70%**, and that is enough to poison clustering. `get_ruling_direction()` returns from two vocabularies — posture-derived (`favored_plaintiff`) and verb-derived (`favorable`) — which deliberately never compare equal so an un-postured memory cannot silently agree with a postured one. That fail-safe was designed and documented this morning as "handled safely but not observed in practice." It has now been observed, and it fires constantly: the largest cluster held `{favorable: 4, favored_plaintiff: 3, favored_defendant: 1, neutral: 1}`, counting three memories as deviating from four memories that describe the same rulings favoring the same party. A meaningful share of the 9 reported deviations are artifacts.

2. **Clusters fragment badly.** 19 clusters from 38 memories; 10 of them singletons, which `build_pattern_evidence()` skips entirely. The cluster key concatenates every matching strategy tag, so more thorough tagging produces narrower buckets — a direct incentive against good extraction.

3. **Pattern evidence counts memories, not rulings.** Hand-classified by ruling, the three transcripts are 6 plaintiff / 5 defendant / 1 neither — balanced, as designed. Counted by memory, they are 13 / 7 / 5, or 52% plaintiff, which reads as exactly the party lean Reynolds was built *not* to have. Verbose rulings outvote terse ones.

4. **One memory has `source_attorney` and `opposing_counsel` inverted** — Okafor recorded as opposing counsel, Lange as ours. 1 of 62, silent, and it pollutes two entity profiles at once.

5. **The query response was lost to a console encoding crash** on the chart emoji in the Confidence Note header. The call completed and was billed; only the printing failed. Does not affect the dashboard.

WHY:
The run was worth doing precisely because it broke things that reading the code could not reveal. Every one of these findings required real extracted data — the posture coverage rate, the cluster size distribution, the memory-versus-ruling weighting, and the attribution inversion are all properties of what the model actually produces, not of what the code says it will do.

Worth noting against this project's pattern of declared-but-unread plumbing: this time the defect is the opposite shape. The code works exactly as written. It is the *data* that does not meet the code's assumption, and the assumption was never checked because there was no data to check it against.

ALTERNATIVES CONSIDERED (if known):
Re-running the query to recover the lost response — declined for now. The confidence numbers it would summarize are distorted by findings 1 and 3, so a clean response would describe dirty inputs. Better to fix posture coverage first and re-query once the numbers mean something.

STILL OPEN / NEEDS REVISITING:
All five findings are open GitHub issues. The most consequential is posture coverage: it is upstream of the deviation noise, and fixing it may resolve much of the confidence distortion without touching the clustering code. Validation-time enforcement (warn when a ruling tag appears without a posture tag) is cheap and diagnostic regardless of which fix is chosen.

The central demo question — whether the engine can learn a *conduct* lean as distinct from a *party* lean — remains **unanswered**. The data cannot currently show it either way.

---

### DECISION: Keep ingestion on Sonnet 4.6 — the posture gap was a prompt problem, not a capability problem
DATE: August 22, 2026
STATUS: confirmed (measured A/B, same transcripts, same prompt, model varied)

WHAT WAS DECIDED:
`ingestion_model` stays `claude-sonnet-4-6` for now. This **defers rather than reverses** the standing decision to route ingestion through a stronger model, and it narrows the reason: that decision assumed interpretation quality was the binding constraint. Measurement says the prompt was.

Christopher raised the question directly — "if the extraction is the most ai intensive part should we be using opus 5 on high there too?" — which is the third time this session he re-derived a decision already in this log (see also the source-type dropdown). Rather than answer from the log, it was run as an experiment, because the log's reasoning had never been tested.

**Results across three runs on the same three transcripts:**

| metric | baseline (old prompt, Sonnet) | Sonnet 4.6 + new prompt | Opus 5 @ high + new prompt |
|---|---:|---:|---:|
| posture coverage | **70%** | **100%** | **100%** |
| verb-derived directions | 7 | 0 | 0 |
| cluster deviations | 9 | 4 | 6 |
| attribution inversions | 1 | 0 | 0 |
| memories extracted | 62 | 56 | 68 |
| tags outside vocabulary | 2 | 2 | **68** |

WHY:
The question the experiment answered was whether the 70% posture gap was an instruction-following failure or a reasoning failure. A prompt fix can close the first; only capability closes the second.

It was entirely the first. Making the posture rule mechanical — trigger on the presence of a ruling tag rather than on the model's judgment about whether a memory "describes a ruling" — took coverage from 70% to 100% **on the same model**. Opus 5 could not improve on that, because there was nothing left to improve.

The downstream effects confirmed the diagnosis rather than merely correlating with it: verb-derived directions went to zero, which eliminated the mixed-vocabulary clusters that were counting memories describing the same ruling as deviating from each other. Deviations fell 9 → 4. The single attribution inversion also disappeared.

**Opus 5's trade-off, measured:** it extracted 21% more memories (68 vs 56) and decomposed them more finely (mean 375 chars vs 516), with more precise descriptions. But 68 of its 219 tags fell outside the controlled vocabulary versus 2 of 148 — it follows the prompt's invitation to use "descriptive tags" far more enthusiastically. Those tags are invisible to the engine, since clustering and scoring both work by intersection with the controlled sets. It also fired 22 drift warnings against Sonnet's 2, which makes the drift detector useless: a real typo would be lost among conformant behavior. Logged separately as its own issue.

Cost was not the deciding factor and should not be presented as one — roughly $0.18 versus $0.31 for three transcripts, or about $1.80 versus $3.10 for a full thirty-transcript demo. The decision is about output quality, and on the metric that mattered the two models are identical.

ALTERNATIVES CONSIDERED (if known):
Switching to Opus 5 and re-ingesting in one step — rejected as an experimental-design error. The prompt had just changed; changing the model simultaneously would have confounded the two and left the permanent per-document cost decided on an assumption. Running both cost about $0.50 total and produced a defensible answer.

Sonnet 5 was noted as a middle option — currently at introductory pricing of $2/$10 per MTok through 2026-08-31, which makes it cheaper than the Sonnet 4.6 in use and more capable. Not tested; worth considering before the intro pricing expires.

STILL OPEN / NEEDS REVISITING:
Revisit when the descriptive-tag question is settled. Opus 5's finer decomposition may prove more valuable at scale, and its vocabulary behavior is a prompt-specification problem rather than a model defect — once `fact_pattern_tags` and `tags` have distinct, stated purposes, the comparison should be re-run.

Cluster fragmentation was untouched by any of this, as expected: 19 clusters in all three runs, with 10–13 singletons that cannot form patterns. That is a clustering-key design problem, not an extraction problem.

The posture mix is still plaintiff-leaning by memory count (10/6/2) against a design target of roughly balanced. Hand-classified by *ruling* the transcripts are 6/5/1, so this is the memory-count weighting distortion rather than a data problem.

---

*(Append new entries below this line, oldest first, using the template above.)*
