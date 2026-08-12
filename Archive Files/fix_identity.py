import json

identity = {
    "name": "Christopher Dudley",
    "current_project": "Building a local-first, private, and persistent cognitive operating system that creates more useful and secure AI agents regardless of which LLM is used",
    "background": [
        "Sales — customer psychology, persuasion, closing, relationship building",
        "Plumbing — systems thinking, problem solving under pressure, practical execution",
        "Army National Guard — operational discipline, execution under constraint, mission focus"
    ],
    "core_principles": [
        "The LLM is replaceable. The continuity layer is the true asset.",
        "Memory and context compound in value over time.",
        "The user owns their intelligence. Not the AI provider.",
        "Local-first architecture protects privacy and permanence.",
        "AI should augment humans, not replace them.",
        "Bounded authority — AI never has unrestricted control."
    ],
    "active_projects": [
        "Cognitive OS — personal demo build"
    ],
    "target_market": [
        "Executives and founders",
        "Operations and sales leaders",
        "Organizations with knowledge retention problems",
        "Expertise-driven businesses"
    ],
    "build_stage": "Pre-revenue. Building personal demo to validate retrieval quality before seeking investment.",
    "business_framework": "Hormozi principles — value creation, offer clarity, acquisition economics. Loaded separately in knowledge base.",
    "investor_status": "Seeking first conversations with tech-focused investors after demo completion.",
    "system_note": "Always ground responses in Christopher's specific context. Never give generic advice that could apply to anyone. Reference his background and project when relevant. Weight practical execution over theory."
}

with open("data/identity.json", "w", encoding="utf-8") as f:
    json.dump(identity, f, indent=2, ensure_ascii=True)

print("Identity file written successfully.")