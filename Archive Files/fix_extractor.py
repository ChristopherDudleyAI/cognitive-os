code = open('ingestion/extractor.py', 'w', encoding='utf-8')
code.write("""import anthropic
import json

class Extractor:

    def __init__(self, api_key: str, model: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def extract(self, raw_input: str) -> list:

        prompt = f\"\"\"You are a memory extraction engine for a cognitive operating system.

Read the following input carefully. This may be personal experience, a conversation transcript, a sales call, a document, scripture, or philosophical text.

Extract every discrete piece of wisdom, principle, decision, or observable pattern that could be valuable as a persistent memory.

OUTCOME DETECTION — CRITICAL:
For any conversational content such as sales calls, meetings, negotiations, or interviews:
- Identify whether each key moment or technique produced a positive, negative, or neutral customer or participant response
- Look for signals such as: agreement, objection, silence, enthusiasm, hesitation, commitment, withdrawal, follow-up requests, price resistance, emotional tone shifts
- Record the outcome alongside the technique or decision that produced it
- If the overall call result is clear (deal closed, deal lost, follow-up scheduled, customer disengaged) record that as a separate outcome memory
- Outcome confidence: verified means clearly stated in the transcript, probable means strongly implied, uncertain means unclear

For biblical or religious texts:
- Preserve the source reference and theological framing exactly as written
- Include both the spiritual principle and its practical application
- Do not neutralize or generalize away from the original meaning

For philosophical or literary texts:
- Preserve the author framing and voice
- Extract the specific principle the author intended
- Include the source when known

For personal experience or decisions:
- Extract discrete decisions, lessons, and observations
- Note outcomes where known

For each extracted item identify:
- What the principle, technique, decision, or insight is
- What the outcome was if detectable
- What category it belongs to: people, resources, risk, relationships, patterns, or context
- What type it is: experience, knowledge, or decision
- Key tags (3-5 words maximum each)
- Importance level: critical, high, medium, or low

Rules:
- One memory equals one discrete idea, technique, or decision
- Do not summarize everything as one memory
- Always attempt outcome detection for conversational content
- Preserve source worldview and framing for texts
- If content has no practical wisdom value skip it
- Be specific not general

Return ONLY a JSON array. No explanation. No preamble. No markdown code blocks. Just the raw JSON array.

Format:
[
  {{
    "memory_text": "description of what happened or the principle",
    "type": "experience|knowledge|decision",
    "category": "people|resources|risk|relationships|patterns|context",
    "importance": "critical|high|medium|low",
    "tags": ["tag1", "tag2", "tag3"],
    "decision_made": true or false,
    "outcome_known": true or false,
    "outcome": "description of what resulted — positive, negative, or neutral with specifics if available",
    "outcome_confidence": "verified|probable|uncertain"
  }}
]

Input to extract from:
{raw_input}\"\"\"

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
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
                lines = cleaned.split("\\n")
                cleaned = "\\n".join(lines[1:-1])
            candidates = json.loads(cleaned)
            return candidates
        except json.JSONDecodeError as e:
            print(f"Parse error: {e}")
            print(f"Raw response: {response_text}")
            return []
""")
code.close()
print("Extractor updated successfully.")