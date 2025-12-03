import faiss
import sqlite3
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path

class AuroraMemVault:
    def __init__(self, persist_dir: Path, embedding_model: str = "all-MiniLM-L6-v2"):
        self.persist_dir = persist_dir
        self.persist_dir.mkdir(exist_ok=True)
        
        self.db_path = self.persist_dir / "memory.db"
        self.index_path = self.persist_dir / "faiss.index"
        
        # Init SQLite
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE,
                content TEXT,
                metadata TEXT,
                embedding BLOB
            )
        """)
        
        # Init FAISS
        self.encoder = SentenceTransformer(embedding_model)
        self.dim = self.encoder.get_sentence_embedding_dimension()
        if self.index_path.exists():
            self.index = faiss.read_index(str(self.index_path))
        else:
            self.index = faiss.IndexFlatL2(self.dim)

    def add_memory(self, key: str, content: str, meta dict = None):
        embedding = self.encoder.encode([content])[0]
        embedding_bytes = embedding.tobytes()
        
        self.conn.execute(
            "INSERT OR REPLACE INTO memories (key, content, metadata, embedding) VALUES (?, ?, ?, ?)",
            (key, content, json.dumps(metadata or {}), embedding_bytes)
        )
        self.conn.commit()
        
        # Update FAISS
        if self.index.ntotal == 0:
            self.index.add(np.array([embedding]))
        else:
            self.index.add(np.array([embedding]))
        faiss.write_index(self.index, str(self.index_path))
