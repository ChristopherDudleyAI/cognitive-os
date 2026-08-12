import chromadb
from chromadb.config import Settings

class VectorDB:

    def __init__(self, db_path="data/chroma.db"):
        self.client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(
                anonymized_telemetry=False
            )
        )

        self.collection = self.client.get_or_create_collection(
            name="legal_memories",
            metadata={
                "hnsw:space": "cosine"
            }
        )

        print("Legal vector database initialized.")

    def _build_where(self, conditions: list):
        # ChromaDB requires multiple filter conditions to be wrapped
        # in an explicit $and operator. A single condition is passed
        # directly. This helper builds the correct shape either way.
        if not conditions:
            return None
        if len(conditions) == 1:
            return conditions[0]
        return {"$and": conditions}

    def add(self, memory: dict):
        memory_id = memory.get('id')
        memory_text = memory.get('memory_text')

        if not memory_id or not memory_text:
            return False

        metadata = {
            "memory_type": memory.get('memory_type') or "operational",
            "practice_area": memory.get('practice_area') or "general",
            "matter_type": memory.get('matter_type') or "general",
            "matter_id": memory.get('matter_id') or "none",
            "importance": memory.get('importance') or "medium",
            "status": memory.get('status') or "active",
            "permission_level": memory.get('permission_level') or "llm_allowed",
            "source_attorney": memory.get('source_attorney') or "unknown",
            "opposing_counsel": memory.get('opposing_counsel') or "none",
            "judge": memory.get('judge') or "none",
            "outcome": memory.get('outcome') or "none",
            "extraction_category": memory.get('extraction_category') or "general"
        }

        existing = self.collection.get(ids=[memory_id])

        if existing['ids']:
            self.collection.update(
                ids=[memory_id],
                documents=[memory_text],
                metadatas=[metadata]
            )
        else:
            self.collection.add(
                ids=[memory_id],
                documents=[memory_text],
                metadatas=[metadata]
            )

        return True

    def search(self,
               query: str,
               practice_area: str = None,
               memory_type: str = None,
               matter_id: str = None,
               n_results: int = 10):

        conditions = [
            {"status": "active"},
            {"permission_level": "llm_allowed"}
        ]

        if practice_area:
            conditions.append({"practice_area": practice_area})

        if memory_type:
            conditions.append({"memory_type": memory_type})

        if matter_id:
            conditions.append({"matter_id": matter_id})

        where = self._build_where(conditions)

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where
            )

            memories = []

            if results['ids'][0]:
                for i, mem_id in enumerate(results['ids'][0]):
                    memories.append({
                        'id': mem_id,
                        'memory_text': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i]
                    })

            return memories

        except Exception as e:
            print(f"Search error: {e}")
            return []

    def search_by_fact_pattern(self,
                                fact_pattern: str,
                                practice_area: str = None,
                                n_results: int = 10):

        conditions = [
            {"status": "active"},
            {"permission_level": "llm_allowed"},
            {"memory_type": "precedent"}
        ]

        if practice_area:
            conditions.append({"practice_area": practice_area})

        where = self._build_where(conditions)

        try:
            results = self.collection.query(
                query_texts=[fact_pattern],
                n_results=n_results,
                where=where
            )

            memories = []

            if results['ids'][0]:
                for i, mem_id in enumerate(results['ids'][0]):
                    memories.append({
                        'id': mem_id,
                        'memory_text': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i]
                    })

            return memories

        except Exception as e:
            print(f"Fact pattern search error: {e}")
            return []

    def count(self):
        return self.collection.count()

    def delete(self, memory_id: str):
        self.collection.delete(ids=[memory_id])