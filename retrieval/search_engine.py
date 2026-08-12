import json
from datetime import datetime

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

        # Ruling context tag clusters for
        # intelligent deviation detection
        self.ruling_type_tags = {
            'objection_sustained',
            'objection_overruled',
            'motion_granted',
            'motion_denied',
            'evidence_admitted',
            'evidence_excluded',
            'sanctions_issued',
            'discovery_ordered'
        }

        self.legal_basis_tags = {
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
            'causation'
        }

        self.proceeding_tags = {
            'deposition_proceeding',
            'motion_hearing',
            'trial_proceeding',
            'summary_judgment',
            'motion_in_limine',
            'discovery_hearing'
        }

        self.strategy_tags = {
            'examination_technique',
            'objection_strategy',
            'motion_strategy',
            'argument_framing',
            'witness_impeachment',
            'document_strategy',
            'deadline_management'
        }

        # Ruling posture — which party a ruling actually benefited.
        # Fixes audit finding #3. MUST stay in sync with structurer.py.
        self.posture_tags = {
            'favored_plaintiff',
            'favored_defendant',
            'favored_neither'
        }

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
        tags = set(
            memory.get('fact_pattern_tags', [])
        )

        legal_basis = tags & self.legal_basis_tags
        proceeding = tags & self.proceeding_tags
        strategy = tags & self.strategy_tags

        cluster_parts = []

        if legal_basis:
            cluster_parts.append(
                '_'.join(sorted(legal_basis))
            )

        if proceeding:
            cluster_parts.append(
                '_'.join(sorted(proceeding))
            )

        if strategy:
            cluster_parts.append(
                '_'.join(sorted(strategy))
            )

        if cluster_parts:
            return '|'.join(cluster_parts)

        # Fall back to extraction category
        return memory.get('extraction_category', 'general')

    def get_ruling_direction(self,
                              memory: dict) -> str:
        tags = set(
            memory.get('fact_pattern_tags', [])
        )
        ruling_tags = tags & self.ruling_type_tags

        favorable = {
            'objection_sustained',
            'motion_granted',
            'evidence_excluded',
            'sanctions_issued',
            'discovery_ordered'
        }
        unfavorable = {
            'objection_overruled',
            'motion_denied',
            'evidence_admitted'
        }

        if ruling_tags & favorable:
            return 'favorable'
        elif ruling_tags & unfavorable:
            return 'unfavorable'

        return 'neutral'

    def build_pattern_evidence(self,
                                top_memories: list,
                                prompt: str,
                                practice_area: str = None
                                ) -> dict:

        evidence = {}

        # Extract key entities from top memories
        judges = set()
        counsels = set()
        practice_areas = set()

        for memory in top_memories:
            if memory.get('judge') and \
               memory['judge'] != 'none':
                judges.add(memory['judge'])
            if memory.get('opposing_counsel') and \
               memory['opposing_counsel'] != 'none':
                counsels.add(memory['opposing_counsel'])
            if memory.get('practice_area'):
                practice_areas.add(
                    memory.get('practice_area')
                )

        all_memories = self.memory_db.get_all_active()

        # Build evidence for each judge
        for judge in judges:
            key = f"judge_{judge.replace(' ', '_').lower()}"
            judge_memories = [
                m for m in all_memories
                if judge.lower() in
                (m.get('judge') or '').lower()
                and m.get('extraction_category') in [
                    'judge_intelligence',
                    'attorney_strategy',
                    'procedural'
                ]
            ]

            if not judge_memories:
                continue

            # Cluster by ruling context
            clusters = {}
            for memory in judge_memories:
                cluster = self.get_context_cluster(memory)
                if cluster not in clusters:
                    clusters[cluster] = []
                clusters[cluster].append(memory)

            # Within each cluster find
            # corroborating and deviating
            total_corroborating = []
            total_deviating = []

            top_ids = [m['id'] for m in top_memories]

            for cluster_key, cluster_memories in clusters.items():
                if len(cluster_memories) < 2:
                    # Single memory in cluster
                    # cannot deviate from itself
                    for m in cluster_memories:
                        if m['id'] in top_ids:
                            total_corroborating.append(
                                m['id']
                            )
                    continue

                # Score each memory in cluster
                scored_cluster = []
                for m in cluster_memories:
                    scored = self.score_memory(
                        m.copy(), prompt,
                        practice_area, None
                    )
                    if scored.get(
                        'retrieval_score', 0
                    ) >= self.minimum_relevance_threshold:
                        scored_cluster.append(scored)

                if not scored_cluster:
                    continue

                # Find majority ruling direction
                # in this cluster
                directions = [
                    self.get_ruling_direction(m)
                    for m in scored_cluster
                ]
                direction_counts = {}
                for d in directions:
                    direction_counts[d] = \
                        direction_counts.get(d, 0) + 1

                majority_direction = max(
                    direction_counts,
                    key=direction_counts.get
                )

                # Classify each memory in cluster
                for m in scored_cluster:
                    direction = self.get_ruling_direction(m)
                    if direction == majority_direction or \
                       direction == 'neutral':
                        total_corroborating.append(m['id'])
                    else:
                        total_deviating.append(m['id'])

            if total_corroborating or total_deviating:
                evidence[key] = {
                    "entity": judge,
                    "entity_type": "judge",
                    "corroborating_count": len(
                        total_corroborating
                    ),
                    "deviating_count": len(
                        total_deviating
                    ),
                    "corroborating_ids": total_corroborating,
                    "deviating_ids": total_deviating,
                    "confidence_level": self.calculate_confidence(
                        len(total_corroborating),
                        len(total_deviating)
                    )
                }

        # Build evidence for opposing counsel
        for counsel in counsels:
            key = f"counsel_{counsel.replace(' ', '_').lower()}"
            counsel_memories = [
                m for m in all_memories
                if counsel.lower() in
                (m.get('opposing_counsel') or '').lower()
                and m.get('extraction_category') in [
                    'opposing_counsel',
                    'attorney_strategy'
                ]
            ]

            if not counsel_memories:
                continue

            clusters = {}
            for memory in counsel_memories:
                cluster = self.get_context_cluster(memory)
                if cluster not in clusters:
                    clusters[cluster] = []
                clusters[cluster].append(memory)

            total_corroborating = []
            total_deviating = []
            top_ids = [m['id'] for m in top_memories]

            for cluster_key, cluster_memories in clusters.items():
                if len(cluster_memories) < 2:
                    for m in cluster_memories:
                        if m['id'] in top_ids:
                            total_corroborating.append(
                                m['id']
                            )
                    continue

                scored_cluster = []
                for m in cluster_memories:
                    scored = self.score_memory(
                        m.copy(), prompt,
                        practice_area, None
                    )
                    if scored.get(
                        'retrieval_score', 0
                    ) >= self.minimum_relevance_threshold:
                        scored_cluster.append(scored)

                if not scored_cluster:
                    continue

                directions = [
                    self.get_ruling_direction(m)
                    for m in scored_cluster
                ]
                direction_counts = {}
                for d in directions:
                    direction_counts[d] = \
                        direction_counts.get(d, 0) + 1

                majority_direction = max(
                    direction_counts,
                    key=direction_counts.get
                )

                for m in scored_cluster:
                    direction = self.get_ruling_direction(m)
                    if direction == majority_direction or \
                       direction == 'neutral':
                        total_corroborating.append(m['id'])
                    else:
                        total_deviating.append(m['id'])

            if total_corroborating or total_deviating:
                evidence[key] = {
                    "entity": counsel,
                    "entity_type": "opposing_counsel",
                    "corroborating_count": len(
                        total_corroborating
                    ),
                    "deviating_count": len(
                        total_deviating
                    ),
                    "corroborating_ids": total_corroborating,
                    "deviating_ids": total_deviating,
                    "confidence_level": self.calculate_confidence(
                        len(total_corroborating),
                        len(total_deviating)
                    )
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

        # Bonus for structured tags present
        if memory.get('fact_pattern_tags'):
            tag_set = set(memory['fact_pattern_tags'])
            structured_tags = (
                self.ruling_type_tags |
                self.legal_basis_tags |
                self.proceeding_tags |
                self.strategy_tags
            )
            structured_match = tag_set & structured_tags
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