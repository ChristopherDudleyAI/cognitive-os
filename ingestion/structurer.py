import uuid
from datetime import datetime
import re
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import vocabulary

class Structurer:

    def __init__(self, default_project: str = "Legal Cognitive OS"):
        self.default_project = default_project

        # Controlled fact_pattern_tag vocabulary. Defined once in
        # vocabulary.py and shared with retrieval/search_engine.py —
        # these were previously duplicated in both files and drifted.
        # Aliased onto the instance so existing attribute access keeps
        # working; vocabulary.py is the place to edit.
        self.ruling_type_tags = vocabulary.RULING_TYPE_TAGS
        self.legal_basis_tags = vocabulary.LEGAL_BASIS_TAGS
        self.proceeding_tags = vocabulary.PROCEEDING_TAGS
        self.strategy_tags = vocabulary.STRATEGY_TAGS
        self.outcome_tags = vocabulary.OUTCOME_TAGS
        self.posture_tags = vocabulary.POSTURE_TAGS

        self.controlled_vocabulary = vocabulary.CONTROLLED_VOCABULARY
        self.tag_checked_categories = vocabulary.TAG_CHECKED_CATEGORIES

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