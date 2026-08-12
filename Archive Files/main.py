import json
import os
from storage.memory_db import MemoryDB
from storage.vector_db import VectorDB
from ingestion.extractor import Extractor
from ingestion.structurer import Structurer
from retrieval.search_engine import SearchEngine

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

def initialize_system(config):
    print("Initializing Legal Cognitive OS...")

    os.makedirs("data", exist_ok=True)

    memory_db = MemoryDB(db_path=config["db_path"])
    vector_db = VectorDB(db_path=config["chroma_path"])
    extractor = Extractor(
        api_key=config["anthropic_api_key"],
        model=config["model"]
    )
    structurer = Structurer(
        default_project=config["default_project"]
    )
    search_engine = SearchEngine(
        memory_db=memory_db,
        vector_db=vector_db,
        config=config
    )

    print(f"System initialized. Memories in database: {memory_db.count()}")

    return memory_db, vector_db, extractor, structurer, search_engine

def ingest_text(text: str,
                source: str,
                extractor: Extractor,
                structurer: Structurer,
                memory_db: MemoryDB,
                vector_db: VectorDB) -> int:

    print(f"Extracting memories from: {source}")
    candidates = extractor.extract(text)
    print(f"Extracted {len(candidates)} memory candidates")

    structured = structurer.structure_batch(
        candidates=candidates,
        source=source
    )
    print(f"Structured {len(structured)} memories")

    saved_count = 0
    for memory in structured:
        try:
            memory_db.save(memory)
            vector_db.add(memory)
            saved_count += 1
        except Exception as e:
            print(f"Failed to save memory: {e}")
            continue

    print(f"Saved {saved_count} memories to database")
    return saved_count

def retrieve_context(prompt: str,
                     search_engine: SearchEngine,
                     practice_area: str = None,
                     memory_type: str = None,
                     judge: str = None,
                     opposing_counsel: str = None,
                     matter_id: str = None) -> dict:

    context = search_engine.retrieve(
        prompt=prompt,
        practice_area=practice_area,
        memory_type=memory_type,
        judge=judge,
        opposing_counsel=opposing_counsel,
        matter_id=matter_id
    )

    return context

if __name__ == "__main__":
    config = load_config()
    memory_db, vector_db, extractor, structurer, search_engine = initialize_system(config)
    print("Legal Cognitive OS ready.")
    print(f"Total memories: {memory_db.count()}")