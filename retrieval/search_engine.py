import json
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import vocabulary

class SearchEngine:

    def __init__(self, memory_db, vector_db,
                 config: dict = None):
        self.memory_db = memory_db
        self.vector_db = vector_db
        self.config = config or {}

        self.relevance_threshold = self.config.get(
            'relevance_threshold', 60
        )
        self.memory_token_budget = self.config.get(
            'memory_token_budget', 3000
        )
        self.memory_type_thresholds = self.config.get(
            'memory_type_thresholds', {
                'precedent': 50,
                'partner_judgment': 50,
                'matter': 65,
                'client': 80,
                'operational': 85
            }
        )
        self.minimum_relevance_threshold = 40

        # Controlled fact_pattern_tag vocabulary. Defined once in
        # vocabulary.py and shared with ingestion/structurer.py — these
        # were previously duplicated in both files and drifted.
        # Aliased onto the instance so existing attribute access keeps
        # working; vocabulary.py is the place to edit.
        self.ruling_type_tags = vocabulary.RULING_TYPE_TAGS
        self.legal_basis_tags = vocabulary.LEGAL_BASIS_TAGS
        self.proceeding_tags = vocabulary.PROCEEDING_TAGS
        self.strategy_tags = vocabulary.STRATEGY_TAGS
        self.outcome_tags = vocabulary.OUTCOME_TAGS
        self.posture_tags = vocabulary.POSTURE_TAGS

    def retrieve(self, prompt: str,
                 practice_area: str = None,
                 memory_type: str = None,
                 matter_id: str = None,
                 judge: str = None,
                 opposing_counsel: str = None,
                 n_candidates: int = 20) -> dict:

        # Step 1 — Semantic search
        semantic_results = self.vector_db.search(
            query=prompt,
            practice_area=practice_area,
            memory_type=memory_type,
            matter_id=matter_id,
            n_results=n_candidates
        )

        # Step 2 — Keyword search
        keyword_results = self.keyword_search(
            prompt=prompt,
            practice_area=practice_area
        )

        # Step 3 — Targeted searches
        targeted_results = []

        if judge:
            judge_memories = self.memory_db.get_by_judge(judge)
            targeted_results.extend(judge_memories)

        if opposing_counsel:
            counsel_memories = self.memory_db.get_by_opposing_counsel(opposing_counsel)
            targeted_results.extend(counsel_memories)

        if matter_id:
            matter_memories = self.memory_db.get_by_matter(matter_id)
            targeted_results.extend(matter_memories)

        # Step 4 — Merge all results
        candidate_pool = self.merge_results(
            semantic_results,
            keyword_results,
            targeted_results
        )

        # Step 5 — Fetch full memory objects
        full_memories = []
        for candidate in candidate_pool:
            memory = self.memory_db.get(candidate['id'])
            if memory:
                memory['search_type'] = candidate.get(
                    'search_type', 'semantic'
                )
                memory['distance'] = candidate.get(
                    'distance', 1.0
                )
                full_memories.append(memory)

        # Step 6 — Score memories
        scored = []
        for memory in full_memories:
            scored_memory = self.score_memory(
                memory, prompt, practice_area, memory_type
            )
            scored.append(scored_memory)

        # Step 7 — Sort by score
        scored.sort(
            key=lambda x: x.get('retrieval_score', 0),
            reverse=True
        )

        # Step 8 — Apply threshold filtering
        # instead of hard count limit
        top_memories = self.apply_threshold_filter(scored)

        # Step 9 — Build pattern evidence
        # using context clustering
        pattern_evidence = self.build_pattern_evidence(
            top_memories=top_memories,
            prompt=prompt,
            practice_area=practice_area
        )

        # Step 10 — Update retrieval counts
        for memory in top_memories:
            self.memory_db.increment_retrieval(
                memory['id']
            )

        # Step 11 — Build context packet
        context_packet = {
            "prompt": prompt,
            "practice_area": practice_area or "general",
            "memory_type_filter": memory_type,
            "judge_filter": judge,
            "opposing_counsel_filter": opposing_counsel,
            "matter_id_filter": matter_id,
            "memories": top_memories,
            "pattern_evidence": pattern_evidence,
            "retrieval_timestamp": datetime.now().isoformat(),
            "memories_used": [m['id'] for m in top_memories],
            "memory_breakdown": self.breakdown_by_type(
                top_memories
            )
        }

        return context_packet

    def apply_threshold_filter(self,
                                scored: list) -> list:

        filtered = []
        estimated_tokens = 0
        token_budget = self.memory_token_budget

        for memory in scored:
            score = memory.get('retrieval_score', 0)
            mem_type = memory.get('memory_type', 'operational')

            # Get type-specific threshold
            type_threshold = self.memory_type_thresholds.get(
                mem_type, self.relevance_threshold
            )

            # Must meet type-specific threshold
            if score < type_threshold:
                continue

            # Estimate token cost of this memory
            text = memory.get('memory_text', '')
            estimated_tokens += len(text.split()) * 1.3

            # Check token budget
            if estimated_tokens > token_budget:
                break

            filtered.append(memory)

        return filtered

    def get_context_cluster(self,
                             memory: dict) -> str:
        # Groups memories by shared CONTEXT so that ruling direction can
        # then be compared within a cluster. The groups that make up the
        # key live in vocabulary.CLUSTER_KEY_GROUPS — edit there, not
        # here, and read the note above it for what is deliberately
        # excluded and why.
        tags = set(
            memory.get('fact_pattern_tags', [])
        )

        cluster_parts = []
        for group in vocabulary.CLUSTER_KEY_GROUPS:
            matched = tags & group
            if matched:
                cluster_parts.append('_'.join(sorted(matched)))

        if cluster_parts:
            return '|'.join(cluster_parts)

        # Fall back to extraction category
        return memory.get('extraction_category', 'general')

    def get_ruling_direction(self,
                              memory: dict) -> str:
        # Prefer the posture tag. It records which party a ruling actually
        # benefited, judged by effect rather than by verb — which is the
        # whole point of audit finding #3. Without it, "plaintiff's motion
        # granted" and "defendant's motion denied" read as opposite
        # directions despite both favoring the plaintiff, so a judge ruling
        # consistently for one side is flagged as deviating from himself.
        #
        # The verb-based fallback below is retained for memories that carry
        # a ruling tag but no posture tag. Its return values are deliberately
        # from a different vocabulary ('favorable' vs 'favored_plaintiff'),
        # so an un-postured memory never compares equal to a postured one.
        # In a mixed cluster that surfaces as a deviation, which is the safe
        # direction to fail in — it lowers confidence rather than inflating it.
        tags = set(
            memory.get('fact_pattern_tags', [])
        )

        posture = tags & vocabulary.POSTURE_TAGS
        if posture:
            direction = sorted(posture)[0]
            # 'favored_neither' marks a purely procedural or administrative
            # ruling. It carries no directional signal, so it maps onto the
            # same 'neutral' that build_pattern_evidence already treats as
            # non-deviating rather than becoming a third direction that
            # everything else deviates from.
            if direction == 'favored_neither':
                return 'neutral'
            return direction

        ruling_tags = tags & vocabulary.RULING_TYPE_TAGS

        if ruling_tags & vocabulary.FAVORABLE_RULING_TAGS:
            return 'favorable'
        elif ruling_tags & vocabulary.UNFAVORABLE_RULING_TAGS:
            return 'unfavorable'

        return 'neutral'

    def ruling_key(self, memory: dict) -> tuple:
        """Identify the distinct ruling a memory describes.

        Extraction deliberately splits one ruling into several memories —
        the rule the judge stated, the relief ordered, the warning
        attached. That is correct for retrieval and wrong for counting:
        it makes one ruling look like three pieces of evidence.

        It is also not evenly wrong. Plaintiff-favorable rulings measured
        1.9-2.3 memories each against 1.5 for defendant-favorable, on two
        dockets written days apart. Counting memories therefore reports a
        plaintiff lean that the rulings themselves do not have, and it
        erased the designed contrast between two judges entirely (#22).

        Memories describing the same ruling share a matter, a ruling
        context, and a direction. Against a hand count of the transcripts
        this key lands within 2 rulings per docket; counting memories was
        off by 15 and 10. Its residual error is a genuine ambiguity, not
        a bias — whether summary judgment granted on two counts of one
        motion is one ruling or two is a question the transcript does not
        settle either.

        `matter_id` falls back to `source` so that memories predating
        matter capture do not all collapse into a single ruling.
        """
        return (
            memory.get('matter_id') or memory.get('source') or 'unknown',
            self.get_context_cluster(memory),
            self.get_ruling_direction(memory),
        )

    def _cluster_evidence(self, memories: list, top_ids: list,
                          prompt: str, practice_area: str = None):
        """Cluster memories by context, collapse each cluster's memories
        onto the rulings they describe, then classify each *ruling* as
        corroborating or deviating from that cluster's majority direction.

        Returns (cluster_records, totals).

        The unit of evidence is a ruling, never a memory — see
        `ruling_key()`. Every record therefore carries two figures:
        `corroborating_count` is rulings and drives confidence;
        `corroborating_memory_count` is how many memories those rulings
        were extracted from. Both are reported so the drop from one to
        the other is visible rather than silent, and the memory IDs are
        preserved untouched so any figure can still be traced to source.

        The per-cluster breakdown is returned, not just the totals. A
        "pattern" in the response brief corresponds to a cluster, not to
        the entity as a whole — reporting only entity totals meant every
        pattern in a seven-pattern answer cited the same numbers, which
        made per-pattern confidence decorative.
        """
        clusters = {}
        for memory in memories:
            clusters.setdefault(
                self.get_context_cluster(memory), []
            ).append(memory)

        cluster_records = []
        corroborating = []
        deviating = []
        corroborating_rulings = 0
        deviating_rulings = 0

        for cluster_key, cluster_memories in clusters.items():
            if len(cluster_memories) < 2:
                # A single memory cannot deviate from itself. It still
                # counts toward the entity total if it was retrieved, but
                # it evidences no pattern — so it is recorded as
                # uncompared rather than as agreement.
                singles = [
                    m['id'] for m in cluster_memories
                    if m['id'] in top_ids
                ]
                corroborating.extend(singles)
                if singles:
                    corroborating_rulings += 1
                    cluster_records.append({
                        "cluster": cluster_key,
                        "compared": False,
                        "reason": "only one memory in this context",
                        "corroborating_count": 1,
                        "deviating_count": 0,
                        "corroborating_memory_count": len(singles),
                        "deviating_memory_count": 0,
                        "corroborating_ids": singles,
                        "deviating_ids": [],
                    })
                continue

            scored = [
                s for s in (
                    self.score_memory(
                        m.copy(), prompt, practice_area, None
                    )
                    for m in cluster_memories
                )
                if s.get('retrieval_score', 0)
                >= self.minimum_relevance_threshold
            ]
            if not scored:
                continue

            # Collapse memories onto the rulings they describe. Direction
            # is part of the key, so every memory grouped under one ruling
            # already agrees on direction — the group cannot be internally
            # split, and reading it off the key is exact rather than a
            # majority vote within the group.
            rulings = {}
            for m in scored:
                rulings.setdefault(self.ruling_key(m), []).append(m)

            if len(rulings) < 2:
                # Several memories, but all describing one ruling. That is
                # one observation restated, not a corroborated pattern, and
                # counting it as agreement is exactly the inflation #22
                # was about.
                ids = [m['id'] for m in scored]
                corroborating.extend(ids)
                corroborating_rulings += 1
                cluster_records.append({
                    "cluster": cluster_key,
                    "compared": False,
                    "reason": (
                        f"{len(ids)} memories, all describing one ruling"
                    ),
                    "corroborating_count": 1,
                    "deviating_count": 0,
                    "corroborating_memory_count": len(ids),
                    "deviating_memory_count": 0,
                    "corroborating_ids": ids,
                    "deviating_ids": [],
                })
                continue

            direction_counts = {}
            for key in rulings:
                d = key[-1]
                direction_counts[d] = direction_counts.get(d, 0) + 1

            majority = max(
                direction_counts, key=direction_counts.get
            )

            c_ids = []
            d_ids = []
            c_rulings = 0
            d_rulings = 0
            for key, group in rulings.items():
                d = key[-1]
                if d == majority or d == 'neutral':
                    c_rulings += 1
                    c_ids.extend(m['id'] for m in group)
                else:
                    d_rulings += 1
                    d_ids.extend(m['id'] for m in group)

            corroborating.extend(c_ids)
            deviating.extend(d_ids)
            corroborating_rulings += c_rulings
            deviating_rulings += d_rulings

            cluster_records.append({
                "cluster": cluster_key,
                "compared": True,
                "majority_direction": majority,
                "direction_counts": direction_counts,
                "corroborating_count": c_rulings,
                "deviating_count": d_rulings,
                "corroborating_memory_count": len(c_ids),
                "deviating_memory_count": len(d_ids),
                "corroborating_ids": c_ids,
                "deviating_ids": d_ids,
                "confidence_level": self.calculate_confidence(
                    c_rulings, d_rulings
                ),
            })

        cluster_records.sort(
            key=lambda r: -(r['corroborating_count']
                            + r['deviating_count'])
        )
        totals = {
            "corroborating_count": corroborating_rulings,
            "deviating_count": deviating_rulings,
            "corroborating_memory_count": len(corroborating),
            "deviating_memory_count": len(deviating),
            "corroborating_ids": corroborating,
            "deviating_ids": deviating,
        }
        return cluster_records, totals

    def build_pattern_evidence(self,
                                top_memories: list,
                                prompt: str,
                                practice_area: str = None
                                ) -> dict:

        judges = set()
        counsels = set()

        for memory in top_memories:
            if memory.get('judge') and memory['judge'] != 'none':
                judges.add(memory['judge'])
            if memory.get('opposing_counsel') and                memory['opposing_counsel'] != 'none':
                counsels.add(memory['opposing_counsel'])

        all_memories = self.memory_db.get_all_active()
        top_ids = [m['id'] for m in top_memories]

        # (key prefix, entity names, memory field, categories that count)
        entity_specs = [
            ('judge', judges, 'judge',
             ['judge_intelligence', 'attorney_strategy', 'procedural']),
            ('counsel', counsels, 'opposing_counsel',
             ['opposing_counsel', 'attorney_strategy']),
        ]

        evidence = {}

        for prefix, names, field, categories in entity_specs:
            for name in names:
                matched = [
                    m for m in all_memories
                    if name.lower() in (m.get(field) or '').lower()
                    and m.get('extraction_category') in categories
                ]
                if not matched:
                    continue

                clusters, totals = self._cluster_evidence(
                    matched, top_ids, prompt, practice_area
                )
                if not (totals['corroborating_ids']
                        or totals['deviating_ids']):
                    continue

                key = f"{prefix}_{name.replace(' ', '_').lower()}"
                evidence[key] = {
                    "entity": name,
                    "entity_type": field,
                    **totals,
                    "confidence_level": self.calculate_confidence(
                        totals['corroborating_count'],
                        totals['deviating_count'],
                    ),
                    "clusters": clusters,
                }

        return evidence

    def passes_relevance_gate(self,
                               memory: dict,
                               entity_name: str,
                               entity_type: str,
                               practice_areas: set,
                               categories: set) -> bool:

        if entity_type == 'judge':
            memory_entity = (
                memory.get('judge') or ''
            ).lower()
        elif entity_type == 'opposing_counsel':
            memory_entity = (
                memory.get('opposing_counsel') or ''
            ).lower()
        else:
            return False

        if entity_name.lower() not in memory_entity:
            return False

        memory_practice = memory.get('practice_area', '')
        if practice_areas and \
           memory_practice not in practice_areas:
            return False

        return True

    def calculate_confidence(self,
                              corroborating: int,
                              deviating: int) -> str:

        total = corroborating + deviating

        if total == 0:
            return "insufficient_data"

        if total < 3:
            return "low"

        corroboration_rate = corroborating / total

        if corroboration_rate >= 0.85 and total >= 10:
            return "high"
        elif corroboration_rate >= 0.70 and total >= 5:
            return "medium"
        elif corroboration_rate >= 0.50:
            return "low"
        else:
            return "contradicted"

    def keyword_search(self, prompt: str,
                       practice_area: str = None
                       ) -> list:

        words = prompt.lower().split()

        stop_words = {
            'the', 'a', 'an', 'and', 'or',
            'but', 'in', 'on', 'at', 'to',
            'for', 'of', 'with', 'by', 'how',
            'what', 'when', 'where', 'why',
            'is', 'are', 'was', 'were', 'be',
            'been', 'being', 'have', 'has',
            'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may',
            'might', 'shall', 'can', 'i', 'my',
            'me', 'we', 'our', 'you', 'your'
        }

        keywords = [
            w for w in words
            if w not in stop_words
            and len(w) > 2
        ]

        if not keywords:
            return []

        all_memories = self.memory_db.get_all_active()

        results = []

        for memory in all_memories:
            text = memory.get(
                'memory_text', ''
            ).lower()
            tags = ' '.join(
                memory.get('tags', [])
            ).lower()
            fact_tags = ' '.join(
                memory.get('fact_pattern_tags', [])
            ).lower()
            attorney = (
                memory.get('source_attorney') or ''
            ).lower()
            judge = (
                memory.get('judge') or ''
            ).lower()
            counsel = (
                memory.get('opposing_counsel') or ''
            ).lower()
            combined = (
                text + ' ' + tags + ' ' +
                fact_tags + ' ' + attorney +
                ' ' + judge + ' ' + counsel
            )

            match_count = sum(
                1 for kw in keywords
                if kw in combined
            )

            if match_count > 0:
                memory['keyword_matches'] = match_count
                results.append(memory)

        results.sort(
            key=lambda x: x.get('keyword_matches', 0),
            reverse=True
        )

        return results[:15]

    def merge_results(self,
                      semantic: list,
                      keyword: list,
                      targeted: list = []) -> list:

        pool = {}

        for item in semantic:
            mem_id = item['id']
            pool[mem_id] = {
                'id': mem_id,
                'search_type': 'semantic',
                'distance': item.get('distance', 1.0)
            }

        for item in keyword:
            mem_id = item['id']
            if mem_id in pool:
                pool[mem_id]['search_type'] = 'both'
            else:
                pool[mem_id] = {
                    'id': mem_id,
                    'search_type': 'keyword',
                    'distance': 0.5
                }

        for item in targeted:
            mem_id = item['id']
            if mem_id in pool:
                pool[mem_id]['search_type'] = 'targeted'
            else:
                pool[mem_id] = {
                    'id': mem_id,
                    'search_type': 'targeted',
                    'distance': 0.3
                }

        return list(pool.values())

    def score_memory(self, memory: dict,
                     prompt: str,
                     practice_area: str = None,
                     memory_type: str = None) -> dict:

        score = 0

        importance_scores = {
            'critical': 40,
            'high': 30,
            'medium': 20,
            'low': 10
        }
        score += importance_scores.get(
            memory.get('importance', 'medium'), 20
        )

        type_scores = {
            'precedent': 25,
            'partner_judgment': 25,
            'matter': 20,
            'client': 15,
            'operational': 10
        }
        score += type_scores.get(
            memory.get('memory_type', 'operational'), 10
        )

        if practice_area and \
           memory.get('practice_area') == practice_area:
            score += 30

        outcome = memory.get('outcome', 'na')
        if outcome in ['won', 'lost', 'settled']:
            score += 20

        if outcome == 'won':
            score += 10

        confidence_scores = {
            'verified': 20,
            'probable': 10,
            'uncertain': 0
        }
        score += confidence_scores.get(
            memory.get('confidence', 'probable'), 10
        )

        retrieval_count = memory.get('retrieval_count', 0)
        if retrieval_count > 10:
            score += 15
        elif retrieval_count > 5:
            score += 10
        elif retrieval_count > 0:
            score += 5

        search_type = memory.get('search_type', 'semantic')
        if search_type == 'targeted':
            score += 30
        elif search_type == 'both':
            score += 20

        distance = memory.get('distance', 1.0)
        semantic_score = int((1 - distance) * 40)
        score += semantic_score

        prompt_lower = prompt.lower()
        if memory.get('judge') and \
           memory['judge'].lower() in prompt_lower:
            score += 25

        if memory.get('opposing_counsel') and \
           memory['opposing_counsel'].lower() in prompt_lower:
            score += 25

        # Bonus for structured tags present. Uses the full controlled
        # vocabulary — this union was previously built inline and omitted
        # outcome and posture tags, so a memory tagged 'strategy_succeeded'
        # or 'favored_plaintiff' earned nothing here despite the extraction
        # prompt requiring those tags.
        if memory.get('fact_pattern_tags'):
            tag_set = set(memory['fact_pattern_tags'])
            structured_match = tag_set & vocabulary.SCORING_TAGS
            if structured_match:
                score += min(len(structured_match) * 3, 15)

        memory['retrieval_score'] = score
        return memory

    def breakdown_by_type(self, memories: list) -> dict:

        breakdown = {
            'matter': 0,
            'client': 0,
            'precedent': 0,
            'partner_judgment': 0,
            'operational': 0
        }

        for memory in memories:
            mem_type = memory.get(
                'memory_type', 'operational'
            )
            if mem_type in breakdown:
                breakdown[mem_type] += 1

        return breakdown

    def retrieve_by_fact_pattern(self,
                                  fact_pattern: str,
                                  practice_area: str = None,
                                  n_results: int = 10
                                  ) -> dict:

        results = self.vector_db.search_by_fact_pattern(
            fact_pattern=fact_pattern,
            practice_area=practice_area,
            n_results=n_results
        )

        full_memories = []
        for result in results:
            memory = self.memory_db.get(result['id'])
            if memory:
                memory['distance'] = result.get(
                    'distance', 1.0
                )
                memory['search_type'] = 'fact_pattern'
                full_memories.append(memory)

        scored = []
        for memory in full_memories:
            scored_memory = self.score_memory(
                memory, fact_pattern, practice_area
            )
            scored.append(scored_memory)

        scored.sort(
            key=lambda x: x.get('retrieval_score', 0),
            reverse=True
        )

        top = self.apply_threshold_filter(scored)

        return {
            "fact_pattern_query": fact_pattern,
            "practice_area": practice_area,
            "memories": top,
            "retrieval_timestamp": datetime.now().isoformat()
        }