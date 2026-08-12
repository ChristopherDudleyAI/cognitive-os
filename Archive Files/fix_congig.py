import json

config = {
    "primary_provider": "claude",
    "fallback_order": ["claude", "openai", "ollama"],
    "claude": {
        "api_key": "PLACEHOLDER",
        "model": "claude-opus-4-5"
    },
    "openai": {
        "api_key": "",
        "model": "gpt-4o"
    },
    "ollama": {
        "base_url": "http://localhost:11434",
        "model": "llama3"
    }
}

with open("config.json", "w") as f:
    json.dump(config, f, indent=2)

print("Config written successfully.")