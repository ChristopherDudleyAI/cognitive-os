import anthropic

class LLMInterface:

    def __init__(self, api_key: str, model: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        print(f"LLM Interface ready. Model: {self.model}")

    def format_evidence_block(self, pattern_evidence: dict) -> str:

        if not pattern_evidence:
            return ""

        lines = ["PATTERN EVIDENCE DATABASE:"]
        lines.append(
            "Use the following evidence counts to accurately state "
            "confidence levels and order your patterns. "
            "Do NOT cite memory IDs in the main analysis. "
            "Only reference counts and confidence levels inline. "
            "Save any ID references for the Confidence Caveat section."
        )
        lines.append("")

        confidence_order = {
            'high': 0,
            'medium': 1,
            'low': 2,
            'contradicted': 3,
            'insufficient_data': 4
        }

        sorted_evidence = sorted(
            pattern_evidence.items(),
            key=lambda x: (
                confidence_order.get(
                    x[1].get('confidence_level', 'low'), 2
                ),
                -x[1].get('corroborating_count', 0)
            )
        )

        for key, evidence in sorted_evidence:
            entity = evidence.get('entity', '')
            entity_type = evidence.get('entity_type', '')
            confidence = evidence.get('confidence_level', 'low')
            corroborating_count = evidence.get('corroborating_count', 0)
            deviating_count = evidence.get('deviating_count', 0)
            deviating_ids = evidence.get('deviating_ids', [])

            confidence_label = {
                'high': 'HIGH CONFIDENCE',
                'medium': 'MEDIUM CONFIDENCE',
                'low': 'LOW CONFIDENCE',
                'contradicted': 'CONTRADICTED',
                'insufficient_data': 'INSUFFICIENT DATA'
            }.get(confidence, 'LOW CONFIDENCE')

            lines.append(
                f"ENTITY: {entity} "
                f"({entity_type.replace('_', ' ').title()})"
            )
            lines.append(f"Confidence: {confidence_label}")
            lines.append(
                f"Corroborating memories: {corroborating_count}"
            )
            lines.append(
                f"Deviating memories: {deviating_count}"
            )

            if deviating_ids:
                lines.append(
                    f"Deviating IDs (for caveat section only): "
                    f"{', '.join(deviating_ids)}"
                )

            lines.append("")

        return "\n".join(lines)

    def format_packet(self, context_packet: dict,
                      prompt: str) -> str:

        sections = []

        sections.append(
            "SYSTEM:\n"
            "You are the intelligence layer of a Legal Cognitive OS.\n"
            "Your job is to reason using retrieved legal memories and "
            "provide specific, actionable intelligence to attorneys.\n\n"

            "TONE — THIS IS THE MOST IMPORTANT INSTRUCTION:\n"
            "Write like a sharp senior partner giving a verbal briefing "
            "to a colleague before a hearing — not like someone writing "
            "a legal memo. Say it once, say it well, move on. "
            "If a point can be made in two sentences, do not use five. "
            "Be direct. Be specific. Use bold to highlight what matters. "
            "The attorney reading this is smart and busy — respect that.\n\n"

            "REQUIRED RESPONSE SKELETON — follow this structure exactly. "
            "Within each section write freely in the tone above:\n\n"

            "---\n"
            "## [Descriptive Title] — Intelligence Brief\n\n"

            "### Direct Answer\n"
            "[Bottom line up front. What does the evidence show.]\n\n"

            "---\n"
            "### Pattern 1: [Name — highest confidence first]\n\n"
            "**Confidence: [HIGH/MEDIUM/LOW] "
            "| [N] corroborating observations "
            "| [N] deviations**\n\n"
            "[Your analysis — direct and specific. "
            "Use bold for key terms and tactical points. "
            "Say it once well.]\n\n"
            "**Tactical Implication:** "
            "[One or two sentences. What the attorney should do.]\n\n"

            "---\n"
            "[Continue for ALL patterns the evidence supports. "
            "No cap on number of patterns. "
            "Order highest confidence first. "
            "Within same confidence level order by corroborating "
            "count descending. "
            "Each pattern must have the confidence line and "
            "tactical implication.]\n\n"

            "---\n"
            "### Strategic Synthesis\n\n"
            "[Tie all patterns together. Be specific to the matter, "
            "judge, and counsel involved. Write like a partner "
            "giving the pre-hearing talk — sharp, direct, actionable. "
            "Do not restate what was already said in the patterns. "
            "Add the connective insight that ties them together.]\n\n"

            "---\n"
            "### 📊 Confidence Note: [HIGH/MEDIUM/LOW]\n\n"
            "[ALWAYS INCLUDE. State overall confidence level in the "
            "header — replace [HIGH/MEDIUM/LOW] with the actual level. "
            "Body: state corroborating and deviating counts, note "
            "patterns should be validated with additional transcripts. "
            "Two sentences maximum. No memory IDs here.]\n\n"

            "### Confidence Caveat\n"
            "[ONLY INCLUDE IF deviating memories exist. "
            "List each pattern with deviations, counts, and "
            "deviating memory IDs. Warn attorney not to treat "
            "deviated patterns as settled conclusions.]\n\n"

            "RULES THAT NEVER CHANGE:\n"
            "- Use --- dividers between every major section\n"
            "- Bold confidence lines at top of each pattern\n"
            "- Bold Tactical Implication labels\n"
            "- Bold key terms and critical points inline\n"
            "- Never include memory IDs outside Confidence Caveat\n"
            "- Always include the Confidence Note with level in header\n"
            "- Only include Confidence Caveat if deviations exist\n"
            "- Do not restate points already made — say it once\n"
            "- Do not invent context not in the memories\n"
        )

        practice_area = context_packet.get('practice_area', 'general')
        judge_filter = context_packet.get('judge_filter')
        counsel_filter = context_packet.get('opposing_counsel_filter')

        context_line = (
            f"QUERY CONTEXT:\nPractice Area: {practice_area}"
        )
        if judge_filter:
            context_line += f"\nJudge Filter: {judge_filter}"
        if counsel_filter:
            context_line += (
                f"\nOpposing Counsel Filter: {counsel_filter}"
            )
        sections.append(context_line)

        pattern_evidence = context_packet.get('pattern_evidence', {})
        if pattern_evidence:
            evidence_block = self.format_evidence_block(
                pattern_evidence
            )
            sections.append(evidence_block)

        memories = context_packet.get('memories', [])

        if memories:
            memory_lines = []
            for mem in memories:
                score = mem.get('retrieval_score', 0)
                mem_type = mem.get('memory_type', '').upper()
                category = mem.get('extraction_category', '').upper()
                importance = mem.get('importance', 'medium').upper()
                practice = mem.get('practice_area', '')
                outcome = mem.get('outcome', 'na')
                judge = mem.get('judge')
                counsel = mem.get('opposing_counsel')
                attorney = mem.get('source_attorney')
                mem_id = mem.get('id', '')
                text = mem.get('memory_text', '')
                confidence = mem.get('confidence', 'probable')

                entry = (
                    f"[{mem_type}] [{category}] [{importance}] "
                    f"[{practice.upper()}] Score:{score} "
                    f"Confidence:{confidence.upper()} ID:{mem_id}\n"
                    f"{text}\n"
                    f"Outcome: {outcome}"
                )

                if judge:
                    entry += f"\nJudge: {judge}"
                if counsel:
                    entry += f"\nOpposing Counsel: {counsel}"
                if attorney:
                    entry += f"\nSource Attorney: {attorney}"

                memory_lines.append(entry)

            sections.append(
                "RETRIEVED LEGAL MEMORIES:\n" +
                "\n---\n".join(memory_lines)
            )
        else:
            sections.append(
                "RETRIEVED LEGAL MEMORIES:\n"
                "No relevant memories found for this query."
            )

        breakdown = context_packet.get('memory_breakdown', {})
        if breakdown:
            breakdown_text = "MEMORY BREAKDOWN: " + ", ".join(
                f"{k}: {v}"
                for k, v in breakdown.items() if v > 0
            )
            sections.append(breakdown_text)

        sections.append(f"QUERY:\n{prompt}")

        return "\n\n".join(sections)

    def query(self, prompt: str,
              context_packet: dict,
              max_tokens: int = 2000) -> str:

        formatted = self.format_packet(context_packet, prompt)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": formatted
                    }
                ]
            )

            return response.content[0].text

        except Exception as e:
            return f"Error: {str(e)}"