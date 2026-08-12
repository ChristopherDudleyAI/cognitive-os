import sqlite3
import json
import uuid
from datetime import datetime

class MemoryDB:

    def __init__(self, db_path="data/memories.db"):
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                memory_type TEXT,
                memory_text TEXT,
                practice_area TEXT,
                matter_type TEXT,
                matter_id TEXT,
                extraction_category TEXT,
                importance TEXT,
                date_created TEXT,
                date_of_event TEXT,
                last_used TEXT,
                retrieval_count INTEGER DEFAULT 0,
                source_attorney TEXT,
                confidence TEXT,
                status TEXT DEFAULT 'active',
                outcome TEXT,
                outcome_date TEXT,
                opposing_counsel TEXT,
                judge TEXT,
                fact_pattern_tags TEXT,
                related_memories TEXT,
                tags TEXT,
                permission_level TEXT
            )
        """)

        conn.commit()
        conn.close()
        print("Legal memory database initialized.")

    def save(self, memory: dict):
        if 'id' not in memory or not memory['id']:
            memory['id'] = str(uuid.uuid4())[:8]

        if 'date_created' not in memory:
            memory['date_created'] = datetime.now().isoformat()

        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO memories
            VALUES (
                :id, :memory_type, :memory_text,
                :practice_area, :matter_type, :matter_id,
                :extraction_category, :importance,
                :date_created, :date_of_event,
                :last_used, :retrieval_count,
                :source_attorney, :confidence, :status,
                :outcome, :outcome_date,
                :opposing_counsel, :judge,
                :fact_pattern_tags, :related_memories,
                :tags, :permission_level
            )
        """, {
            'id': memory.get('id'),
            'memory_type': memory.get('memory_type', 'operational'),
            'memory_text': memory.get('memory_text'),
            'practice_area': memory.get('practice_area', 'general'),
            'matter_type': memory.get('matter_type', 'general'),
            'matter_id': memory.get('matter_id'),
            'extraction_category': memory.get('extraction_category'),
            'importance': memory.get('importance', 'medium'),
            'date_created': memory.get('date_created'),
            'date_of_event': memory.get('date_of_event'),
            'last_used': memory.get('last_used'),
            'retrieval_count': memory.get('retrieval_count', 0),
            'source_attorney': memory.get('source_attorney'),
            'confidence': memory.get('confidence', 'probable'),
            'status': memory.get('status', 'active'),
            'outcome': memory.get('outcome'),
            'outcome_date': memory.get('outcome_date'),
            'opposing_counsel': memory.get('opposing_counsel'),
            'judge': memory.get('judge'),
            'fact_pattern_tags': json.dumps(memory.get('fact_pattern_tags', [])),
            'related_memories': json.dumps(memory.get('related_memories', [])),
            'tags': json.dumps(memory.get('tags', [])),
            'permission_level': memory.get('permission_level', 'llm_allowed')
        })

        conn.commit()
        conn.close()
        return memory['id']

    def get(self, memory_id: str):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM memories WHERE id = ?",
            (memory_id,)
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            return self.row_to_dict(row)
        return None

    def get_all_active(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM memories
            WHERE status = 'active'
            AND permission_level = 'llm_allowed'
            ORDER BY date_created DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        return [self.row_to_dict(r) for r in rows]

    def get_by_matter(self, matter_id: str):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM memories
            WHERE matter_id = ?
            AND status = 'active'
            ORDER BY date_created DESC
        """, (matter_id,))

        rows = cursor.fetchall()
        conn.close()

        return [self.row_to_dict(r) for r in rows]

    def get_by_practice_area(self, practice_area: str):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM memories
            WHERE practice_area = ?
            AND status = 'active'
            ORDER BY importance DESC
        """, (practice_area,))

        rows = cursor.fetchall()
        conn.close()

        return [self.row_to_dict(r) for r in rows]

    def get_by_judge(self, judge: str):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM memories
            WHERE judge LIKE ?
            AND status = 'active'
        """, (f"%{judge}%",))

        rows = cursor.fetchall()
        conn.close()

        return [self.row_to_dict(r) for r in rows]

    def get_by_opposing_counsel(self, counsel: str):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM memories
            WHERE opposing_counsel LIKE ?
            AND status = 'active'
        """, (f"%{counsel}%",))

        rows = cursor.fetchall()
        conn.close()

        return [self.row_to_dict(r) for r in rows]

    def count(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM memories")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def increment_retrieval(self, memory_id: str):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE memories
            SET retrieval_count = retrieval_count + 1,
                last_used = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), memory_id))

        conn.commit()
        conn.close()

    def row_to_dict(self, row):
        columns = [
            'id', 'memory_type', 'memory_text',
            'practice_area', 'matter_type', 'matter_id',
            'extraction_category', 'importance',
            'date_created', 'date_of_event',
            'last_used', 'retrieval_count',
            'source_attorney', 'confidence', 'status',
            'outcome', 'outcome_date',
            'opposing_counsel', 'judge',
            'fact_pattern_tags', 'related_memories',
            'tags', 'permission_level'
        ]

        memory = dict(zip(columns, row))

        for field in ['fact_pattern_tags', 'related_memories', 'tags']:
            if memory.get(field):
                try:
                    memory[field] = json.loads(memory[field])
                except:
                    memory[field] = []

        return memory