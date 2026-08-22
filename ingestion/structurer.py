import uuid
from datetime import datetime
import re

class Structurer:

    def __init__(self, default_project: str = "Legal Cognitive OS"):
        self.default_project = default_project

        # Controlled fact_pattern_tag vocabulary — MUST stay in sync
        # with the same sets in retrieval/search_engine.py. Clustering
        # and deviation detection only work on tags from this vocabulary.
        self.ruling_type_tags = {
            'objection_sustained', 'objection_overruled',
            'motion_granted', 'motion_denied',
            'evidence_admitted', 'evidence_excluded',
            'sanctions_issued', 'discovery_ordered'
        }
        self.legal_basis_tags = {
            'foundation_objection', 'speculation_objection',
            'hearsay_objection', 'assumes_facts_objection',
            'mischaracterization_objection', 'relevance_objection',
            'daubert_standard', 'spoliation', 'privilege_claim',
            'deadline_violation', 'standard_of_care', 'causation'
        }
        self.proceeding_tags = {
            'deposition_proceeding', 'motion_hearing',
            'trial_proceeding', 'summary_judgment',
            'motion_in_limine', 'discovery_hearing'
        }
        self.strategy_tags = {
            'examination_technique', 'objection_strategy',
            'motion_strategy', 'argument_framing',
            'witness_impeachment', 'document_strategy',
            'deadline_management'
        }
        self.outcome_tags = {
            'strategy_succeeded', 'strategy_failed', 'strategy_partial',
            'tactic_succeeded', 'tactic_failed'
        }

        # Ruling posture — which party a ruling actually benefited.
        # Fixes audit finding #3. MUST stay in sync with search_engine.py.
        self.posture_tags = {
            'favored_plaintiff', 'favored_defendant', 'favored_neither'
        }

        self.controlled_vocabulary = (
            self.ruling_type_tags
            | self.legal_basis_tags
            | self.proceeding_tags
            | self.strategy_tags
            | self.outcome_tags
            | self.posture_tags
        )

        # Categories whose memories the clustering engine relies on —
        # unrecognized tags in these are worth warning about.
        self.tag_checked_categories = {
            'judge_intelligence',
            'attorney_strategy',
            'opposing_counsel',
            'procedural'
        }

    def _normalize_tag(self, tag) -> str:
        if not isinstance(tag, str):
            return ""
        t = tag.strip().lower()
        t = t.replace(' ', '_').replace('-', '_')
        t = re.sub(r'_+', '_', t)
        t = t.strip('_')
        return t

    def _normalize_name(self, name):
        if not name or not isinstance(name, str):
            return name
        cleaned = re.sub(r'\s+', ' ', name).strip()
        return cleaned if cleaned else None

    def structure(self, candidate: dict,
                  source: str = "manual",
                  source_type: str = None,
                  matter_id: str = None,
                  date_of_event: str = None) -> dict:

        memory_id = "mem_" + str(uuid.uuid4())[:8]
        now = datetime.now().isoformat()

        # matter_id, source, source_type and date_of_event come from the
        # ingest form, not from the extractor. The model cannot know a
        # firm's matter numbering, which document it is reading, or when
        # the underlying event happened — so these are supplied by the
        # caller and take precedence over anything the model emitted.
        memory = {
            "id": memory_id,
            "memory_type": candidate.get('memory_type', 'operational'),
            "memory_text": candidate.get('memory_text', '').strip(),
            "practice_area": candidate.get('practice_area', 'general'),
            "matter_type": candidate.get('matter_type', 'general'),
            "matter_id": matter_id or candidate.get('matter_id') or None,
            "source": source,
            "source_type": source_type,
            "extraction_category": candidate.get('extraction_category', 'general'),
            "importance": candidate.get('importance', 'medium'),
            "date_created": now,
            "date_of_event": date_of_event or candidate.get('date_of_event') or now,
            "last_used": None,
            "retrieval_count": 0,
            "source_attorney": candidate.get('source_attorney', None),
            "confidence": candidate.get('confidence', 'probable'),
            "status": candidate.get('status', 'active'),
            "outcome": candidate.get('outcome', 'na'),
            "outcome_date": candidate.get('outcome_date', None),
            "opposing_counsel": candidate.get('opposing_counsel', None),
            "judge": candidate.get('judge', None),
            "fact_pattern_tags": candidate.get('fact_pattern_tags', []),
            "related_memories": candidate.get('related_memories', []),
            "tags": candidate.get('tags', []),
            "permission_level": candidate.get('permission_level', 'llm_allowed')
        }

        memory = self.validate(memory)

        return memory

    def validate(self, memory: dict) -> dict:

        valid_memory_types = [
            'matter',
            'client',
            'precedent',
            'partner_judgment',
            'operational'
        ]
        if memory['memory_type'] not in valid_memory_types:
            memory['memory_type'] = 'operational'

        valid_practice_areas = [
            'litigation',
            'transactional',
            'family',
            'criminal',
            'estate',
            'employment',
            'real_estate',
            'general'
        ]
        if memory['practice_area'] not in valid_practice_areas:
            memory['practice_area'] = 'general'

        valid_importance = [
            'critical',
            'high',
            'medium',
            'low'
        ]
        if memory['importance'] not in valid_importance:
            memory['importance'] = 'medium'

        valid_status = [
            'active',
            'archived',
            'conflicted',
            'pending_review'
        ]
        if memory['status'] not in valid_status:
            memory['status'] = 'active'

        valid_confidence = [
            'verified',
            'probable',
            'uncertain'
        ]
        if memory['confidence'] not in valid_confidence:
            memory['confidence'] = 'probable'

        valid_outcomes = [
            'won',
            'lost',
            'settled',
            'pending',
            'na'
        ]
        if memory['outcome'] not in valid_outcomes:
            memory['outcome'] = 'na'

        valid_extraction_categories = [
            'case_intelligence',
            'attorney_strategy',
            'judge_intelligence',
            'opposing_counsel',
            'witness_intelligence',
            'client_intelligence',
            'fact_pattern',
            'procedural',
            'general'
        ]
        if memory['extraction_category'] not in valid_extraction_categories:
            memory['extraction_category'] = 'general'

        if not memory['memory_text']:
            memory['status'] = 'pending_review'

        if not isinstance(memory['tags'], list):
            memory['tags'] = []

        if not isinstance(memory['fact_pattern_tags'], list):
            memory['fact_pattern_tags'] = []

        if not isinstance(memory['related_memories'], list):
            memory['related_memories'] = []

        # --- FIX #2: normalize entity names so formatting drift
        # ("Judge  Caldwell" vs "Judge Caldwell") doesn't fragment
        # the pattern-evidence base. Does NOT strip honorifics —
        # canonical naming in transcripts is still required (see note).
        memory['judge'] = self._normalize_name(memory.get('judge'))
        memory['opposing_counsel'] = self._normalize_name(
            memory.get('opposing_counsel')
        )
        memory['source_attorney'] = self._normalize_name(
            memory.get('source_attorney')
        )

        # --- FIX #1: normalize fact_pattern_tags to controlled
        # formatting, and warn on unrecognized tags for the memory
        # categories the clustering engine depends on. Tags are
        # normalized but NOT dropped (descriptive tags are legitimate
        # for non-clustering categories).
        normalized_tags = []
        for tag in memory['fact_pattern_tags']:
            norm = self._normalize_tag(tag)
            if norm:
                normalized_tags.append(norm)
        memory['fact_pattern_tags'] = normalized_tags

        if memory['extraction_category'] in self.tag_checked_categories:
            unrecognized = [
                t for t in normalized_tags
                if t not in self.controlled_vocabulary
            ]
            if unrecognized:
                preview = memory['memory_text'][:60]
                print(
                    f"[TAG WARNING] {memory['id']} "
                    f"({memory['extraction_category']}): "
                    f"tags not in controlled vocabulary "
                    f"{unrecognized} — check for typo/drift. "
                    f"Memory: {preview}..."
                )

        return memory

    def structure_batch(self, candidates: list,
                        source: str = "manual",
                        source_type: str = None,
                        matter_id: str = None,
                        date_of_event: str = None) -> list:

        structured = []

        for candidate in candidates:
            try:
                memory = self.structure(
                    candidate,
                    source=source,
                    source_type=source_type,
                    matter_id=matter_id,
                    date_of_event=date_of_event
                )
                structured.append(memory)
            except Exception as e:
                print(f"Failed to structure candidate: {e}")
                continue

        return structured