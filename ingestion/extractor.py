import anthropic
import json

class Extractor:

    # Extraction branches. Each source type gets its own prompt builder,
    # chunk size, and default confidence, because different source types
    # contain fundamentally different intelligence — a transcript has
    # rulings and objections, an attorney debrief has judgment and
    # reasoning. Only the court-transcript branch is built so far; adding
    # another means adding an entry here and its prompt builder, not
    # editing the extraction flow.
    #
    # 'prompt' names a method on this class. Keep the output JSON contract
    # identical across branches — storage, retrieval and clustering all
    # depend on it. See docs/ARCHITECTURE.md sections 1 and 6.
    BRANCHES = {
        'court_transcript': {
            'label': 'Court transcript / deposition',
            'prompt': '_court_transcript_prompt',
            'chunk_word_limit': 1500,
            'default_confidence': 'probable',
        },
    }

    DEFAULT_BRANCH = 'court_transcript'

    def __init__(self, api_key: str, model: str,
                 ingestion_model: str = None):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.ingestion_model = ingestion_model or model
        self.chunk_word_limit = 1500

    def get_branch(self, source_type: str = None) -> dict:
        return self.BRANCHES.get(
            source_type or self.DEFAULT_BRANCH,
            self.BRANCHES[self.DEFAULT_BRANCH]
        )

    def extract(self, raw_input: str, source_type: str = None) -> list:

        branch = self.get_branch(source_type)
        chunk_limit = branch.get(
            'chunk_word_limit', self.chunk_word_limit
        )

        word_count = len(raw_input.split())

        if word_count > chunk_limit:
            print(
                f"Input is {word_count} words. "
                f"Splitting into chunks for extraction."
            )
            return self.chunk_and_extract(
                raw_input, source_type=source_type
            )

        return self._extract_single(raw_input, source_type=source_type)

    def _extract_single(self, raw_input: str,
                        source_type: str = None) -> list:

        branch = self.get_branch(source_type)
        prompt = getattr(self, branch['prompt'])(raw_input)

        return self._call_model(prompt)

    def _court_transcript_prompt(self, raw_input: str) -> str:

        prompt = f"""You are a legal memory extraction engine for a law firm's cognitive operating system.

Read the following input carefully. This may be a court transcript, deposition, hearing, client meeting, attorney notes, case file, or any legal document.

Your job is to extract every discrete piece of legal intelligence that could be valuable as a persistent memory for the firm.

Extract memories across ALL of these categories where present:

CASE & MATTER INTELLIGENCE:
- Case name, number, court, jurisdiction, judge
- Case type and practice area
- Matter stage and timeline
- Opposing counsel name and firm
- Witnesses identified
- Key dates and deadlines
- Damages claimed or discussed
- Settlement amounts discussed
- Final outcome if known
- Case strengths and weaknesses
- Theories of liability

ATTORNEY STRATEGY & JUDGMENT:
- Opening and closing argument structure
- Examination strategy
- Objection patterns and outcomes
- Motions filed and results
- Arguments that landed or failed
- How attorney handles hostile or evasive witnesses
- Impeachment techniques
- Theme and narrative construction
- Settlement posture and timing
- Negotiation approach and concessions
- Document introduction strategy

JUDGE INTELLIGENCE:
- Judge's procedural preferences
- Judge's temperament
- How judge responds to objections
- Evidentiary rulings
- Questions from the bench
- Judge's apparent sympathies
- Patterns in rulings

OPPOSING COUNSEL INTELLIGENCE:
- Examination style
- Objection strategy
- Weaknesses exposed
- Arguments favored or avoided
- Negotiation behavior
- Preparation level
- Tactics used and effectiveness

WITNESS INTELLIGENCE:
- Credibility assessment
- Demeanor under direct and cross
- Vulnerabilities identified
- Inconsistencies in testimony
- How witness handled pressure
- Key admissions extracted
- Expert witness methodology

CLIENT INTELLIGENCE:
- Communication style
- Risk tolerance
- Emotional state
- Priorities
- Credibility as witness
- Version of events
- Gaps in account

FACT PATTERN LIBRARY:
- Core factual dispute
- Key documents referenced
- Chain of custody issues
- Contractual terms disputed
- Breach facts established
- Damages calculation methodology
- Causation arguments
- Affirmative defenses
- Analogous fact patterns for future retrieval

PROCEDURAL & OPERATIONAL:
- Local rules applied
- Court filing preferences
- Discovery disputes and resolutions
- Privilege issues
- Lessons learned

STRUCTURED TAGGING REQUIREMENTS:

For JUDGE INTELLIGENCE memories, fact_pattern_tags MUST include ALL applicable tags from these categories:

Ruling type (use exact tag):
- "objection_sustained"
- "objection_overruled"
- "motion_granted"
- "motion_denied"
- "evidence_admitted"
- "evidence_excluded"
- "sanctions_issued"
- "discovery_ordered"

Legal basis (use exact tag):
- "foundation_objection"
- "speculation_objection"
- "hearsay_objection"
- "assumes_facts_objection"
- "mischaracterization_objection"
- "relevance_objection"
- "daubert_standard"
- "spoliation"
- "privilege_claim"
- "deadline_violation"
- "standard_of_care"
- "causation"

Proceeding context (use exact tag):
- "deposition_proceeding"
- "motion_hearing"
- "trial_proceeding"
- "summary_judgment"
- "motion_in_limine"
- "discovery_hearing"

RULING POSTURE — REQUIRED on any memory describing a judicial ruling.
Add exactly ONE of these tags to fact_pattern_tags, indicating which party
the ruling actually benefited. Determine this by EFFECT, not by the verb —
combine WHO sought or objected with HOW the judge ruled:

- "favored_plaintiff"  (plaintiff's motion granted, OR defendant's objection/motion denied)
- "favored_defendant"  (defendant's motion granted, OR plaintiff's objection/motion denied)
- "favored_neither"    (purely procedural/administrative/neutral ruling)

"Objection sustained" favors whoever raised the objection. "Objection overruled"
favors the opposing party. Always reason: who benefited from this outcome?
If the parties are labeled differently (petitioner/respondent), treat the
initiating/claiming party as plaintiff and the responding party as defendant.

For ATTORNEY STRATEGY memories, fact_pattern_tags MUST include:

Technique type (use exact tag):
- "examination_technique"
- "objection_strategy"
- "motion_strategy"
- "argument_framing"
- "witness_impeachment"
- "document_strategy"
- "deadline_management"

Outcome (use exact tag):
- "strategy_succeeded"
- "strategy_failed"
- "strategy_partial"

For OPPOSING COUNSEL memories, fact_pattern_tags MUST include:
- The specific tactic observed
- "tactic_succeeded" or "tactic_failed"
- The proceeding type

For all other memory types use descriptive tags that accurately reflect the specific content.

For each extracted memory identify:
- memory_text: clear factual description of the intelligence
- memory_type: one of [matter, client, precedent, partner_judgment, operational]
- extraction_category: one of [case_intelligence, attorney_strategy, judge_intelligence, opposing_counsel, witness_intelligence, client_intelligence, fact_pattern, procedural]
- practice_area: one of [litigation, transactional, family, criminal, estate, employment, real_estate, general]
- matter_type: specific type such as contract_dispute, personal_injury, divorce, criminal_defense, merger, employment_discrimination, medical_malpractice, premises_liability, etc.
- importance: one of [critical, high, medium, low]
- outcome: one of [won, lost, settled, pending, na]
- source_attorney: name of attorney if identifiable, otherwise null
- opposing_counsel: name of opposing counsel if identifiable, otherwise null
- judge: name of judge if identifiable, otherwise null
- fact_pattern_tags: list of structured tags following the requirements above — these are critical for pattern recognition
- tags: list of 3-6 general searchable tags

Rules:
- One memory equals one discrete piece of intelligence
- Be specific and factual, not general
- If a name is mentioned capture it
- If an outcome is mentioned capture it
- If a strategy worked or failed capture both the strategy and the result
- Do not summarize everything as one memory
- Extract as many discrete memories as the content supports
- Follow the structured tagging requirements exactly — tags are used for pattern clustering

Return ONLY a JSON array. No explanation. No preamble. No markdown code blocks. Just the raw JSON array.

Format:
[
  {{
    "memory_text": "specific legal intelligence extracted",
    "memory_type": "matter|client|precedent|partner_judgment|operational",
    "extraction_category": "case_intelligence|attorney_strategy|judge_intelligence|opposing_counsel|witness_intelligence|client_intelligence|fact_pattern|procedural",
    "practice_area": "litigation|transactional|family|criminal|estate|employment|real_estate|general",
    "matter_type": "specific matter type",
    "importance": "critical|high|medium|low",
    "outcome": "won|lost|settled|pending|na",
    "source_attorney": "attorney name or null",
    "opposing_counsel": "opposing counsel name or null",
    "judge": "judge name or null",
    "fact_pattern_tags": ["structured_tag1", "structured_tag2", "structured_tag3"],
    "tags": ["tag1", "tag2", "tag3"]
  }}
]

Input to extract from:
{raw_input}"""

        return prompt

    def _call_model(self, prompt: str) -> list:

        response = self.client.messages.create(
            model=self.ingestion_model,
            max_tokens=7000,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        response_text = response.content[0].text

        try:
            cleaned = response_text.strip()
            if cleaned.startswith("```"):
                lines = cleaned.split("\n")
                cleaned = "\n".join(lines[1:-1])
            candidates = json.loads(cleaned)
            return candidates
        except json.JSONDecodeError as e:
            print(f"Parse error: {e}")
            print(f"Raw response: {response_text[:500]}")
            return []

    def chunk_and_extract(self, raw_input: str,
                          source_type: str = None) -> list:

        branch = self.get_branch(source_type)

        words = raw_input.split()
        total_words = len(words)
        chunk_size = branch.get(
            'chunk_word_limit', self.chunk_word_limit
        )
        overlap = 150

        chunks = []
        start = 0

        while start < total_words:
            end = min(start + chunk_size, total_words)
            chunk_words = words[start:end]
            chunk_text = ' '.join(chunk_words)
            chunks.append(chunk_text)

            if end >= total_words:
                break

            start = end - overlap

        print(f"Split into {len(chunks)} chunks.")

        all_candidates = []
        seen_texts = set()

        for i, chunk in enumerate(chunks):
            print(
                f"Extracting chunk {i + 1} "
                f"of {len(chunks)}..."
            )
            candidates = self._extract_single(
                chunk, source_type=source_type
            )
            print(
                f"Chunk {i + 1} returned "
                f"{len(candidates)} memories."
            )

            for candidate in candidates:
                text = candidate.get(
                    'memory_text', ''
                ).strip()
                text_key = text[:100].lower()

                if text_key not in seen_texts:
                    seen_texts.add(text_key)
                    all_candidates.append(candidate)

        print(
            f"Total unique memories extracted: "
            f"{len(all_candidates)}"
        )
        return all_candidates