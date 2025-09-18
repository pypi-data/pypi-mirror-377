import json
import os
import sqlite3
import threading
import time
from typing import Any, Dict, Iterable, List, Optional, Tuple


def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row

    # Optimize for performance and concurrency
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA cache_size=10000;")  # 10MB cache
    conn.execute("PRAGMA temp_store=MEMORY;")
    conn.execute("PRAGMA mmap_size=268435456;")  # 256MB mmap
    conn.execute("PRAGMA optimize;")  # Auto-optimize query planner

    return conn


SCHEMA_SQL = [
    # projects
    """
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        created_at INTEGER NOT NULL
    );
    """,
    # messages
    """
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        agent TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        image_path TEXT,
        created_at INTEGER NOT NULL,
        FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_messages_project_created ON messages(project_id, created_at DESC);",
    "CREATE INDEX IF NOT EXISTS idx_messages_agent_time ON messages(agent, created_at DESC);",
    "CREATE INDEX IF NOT EXISTS idx_messages_content_search ON messages(project_id, content);",
    # webhooks
    """
    CREATE TABLE IF NOT EXISTS webhooks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        url TEXT NOT NULL,
        secret TEXT NOT NULL,
        events TEXT NOT NULL,
        active INTEGER NOT NULL DEFAULT 1,
        created_at INTEGER NOT NULL,
        FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_webhooks_project ON webhooks(project_id);",
    "CREATE INDEX IF NOT EXISTS idx_webhooks_active ON webhooks(active, project_id);",
    # agent status (presence + RL state)
    """
    CREATE TABLE IF NOT EXISTS agent_status (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent TEXT NOT NULL,
        project_id INTEGER,
        status TEXT,
        details TEXT,
        last_seen INTEGER,
        rate_tokens REAL,
        rate_refill_ts INTEGER,
        UNIQUE(agent, project_id)
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_agent_status_lookup ON agent_status(agent, project_id);",
    "CREATE INDEX IF NOT EXISTS idx_agent_status_last_seen ON agent_status(last_seen DESC);",
    # floor control
    """
    CREATE TABLE IF NOT EXISTS floors (
        project_id INTEGER PRIMARY KEY,
        holder_agent TEXT,
        expires_at INTEGER
    );
    """,
    # digests
    """
    CREATE TABLE IF NOT EXISTS digests (
        project_id INTEGER PRIMARY KEY,
        version INTEGER NOT NULL,
        content TEXT NOT NULL,
        updated_at INTEGER NOT NULL,
        FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
    );
    """,
    # docs + chunks
    """
    CREATE TABLE IF NOT EXISTS docs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        title TEXT NOT NULL,
        source TEXT,
        version INTEGER NOT NULL DEFAULT 1,
        created_at INTEGER NOT NULL
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_docs_title ON docs(title);",
    """
    CREATE TABLE IF NOT EXISTS doc_chunks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doc_id INTEGER NOT NULL,
        chunk_index INTEGER NOT NULL,
        text TEXT NOT NULL,
        sha256 TEXT NOT NULL,
        created_at INTEGER NOT NULL,
        UNIQUE(doc_id, chunk_index),
        FOREIGN KEY(doc_id) REFERENCES docs(id) ON DELETE CASCADE
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_doc_chunks_doc ON doc_chunks(doc_id);",
    # FTS5 for doc search
    """
    CREATE VIRTUAL TABLE IF NOT EXISTS docs_fts USING fts5(
        content,
        doc_id UNINDEXED,
        chunk_index UNINDEXED,
        tokenize='porter'
    );
    """,
]


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        self._conn = _connect(db_path)
        self._lock = threading.RLock()
        self._check_fts5_availability()
        self.bootstrap()

    def _check_fts5_availability(self) -> None:
        """Check if FTS5 is available in SQLite. Fail fast if not."""
        try:
            with self._lock:
                cur = self._conn.cursor()
                cur.execute("CREATE VIRTUAL TABLE fts5_test USING fts5(content);")
                cur.execute("DROP TABLE fts5_test;")
                self._conn.commit()
        except Exception as e:
            raise RuntimeError(
                "SQLite FTS5 extension is not available. "
                "FTS5 is required for document search functionality. "
                f"Error: {e}. "
                "Please ensure you're using Python ≥3.11 with a complete SQLite installation."
            ) from e

    def bootstrap(self) -> None:
        with self._lock:
            cur = self._conn.cursor()
            for sql in SCHEMA_SQL:
                cur.execute(sql)
            self._conn.commit()

    def _execute(self, sql: str, params: Tuple = ()) -> sqlite3.Cursor:
        with self._lock:
            cur = self._conn.cursor()
            cur.execute(sql, params)
            self._conn.commit()
            return cur

    def _query(self, sql: str, params: Tuple = ()) -> List[sqlite3.Row]:
        with self._lock:
            cur = self._conn.cursor()
            cur.execute(sql, params)
            return cur.fetchall()

    # Projects
    def create_project(self, name: str, description: Optional[str]) -> int:
        ts = int(time.time() * 1000)
        cur = self._execute(
            "INSERT INTO projects(name, description, created_at) VALUES(?,?,?)",
            (name, description or "", ts),
        )
        return int(cur.lastrowid)

    def list_projects(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        rows = self._query(
            "SELECT id, name, description, created_at FROM projects ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )
        return [dict(r) for r in rows]

    # Messages
    def add_message(
        self,
        project_id: int,
        agent: str,
        role: str,
        content: str,
        image_path: Optional[str] = None,
    ) -> int:
        ts = int(time.time() * 1000)
        cur = self._execute(
            "INSERT INTO messages(project_id, agent, role, content, image_path, created_at) VALUES(?,?,?,?,?,?)",
            (project_id, agent, role, content, image_path, ts),
        )
        return int(cur.lastrowid)

    def get_recent_messages(
        self, project_id: int, limit: int = 50, before_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        if before_id:
            rows = self._query(
                "SELECT * FROM messages WHERE project_id=? AND id < ? ORDER BY id DESC LIMIT ?",
                (project_id, before_id, limit),
            )
        else:
            rows = self._query(
                "SELECT * FROM messages WHERE project_id=? ORDER BY id DESC LIMIT ?",
                (project_id, limit),
            )
        return [dict(r) for r in rows]

    def search_messages(
        self, project_id: int, query: str, limit: int = 50, offset: int = 0
    ) -> List[Dict[str, Any]]:
        like = f"%{query}%"
        rows = self._query(
            "SELECT * FROM messages WHERE project_id=? AND content LIKE ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (project_id, like, limit, offset),
        )
        return [dict(r) for r in rows]

    # Webhooks
    def register_webhook(self, project_id: int, url: str, secret: str, events: List[str]) -> int:
        ts = int(time.time() * 1000)
        cur = self._execute(
            "INSERT INTO webhooks(project_id, url, secret, events, active, created_at) VALUES(?,?,?,?,1,?)",
            (project_id, url, secret, json.dumps(events or []), ts),
        )
        return int(cur.lastrowid)

    def list_webhooks(self, project_id: int) -> List[Dict[str, Any]]:
        rows = self._query(
            "SELECT id, url, secret, events, active, created_at FROM webhooks WHERE project_id=? ORDER BY id DESC",
            (project_id,),
        )
        result = []
        for r in rows:
            item = dict(r)
            item["events"] = json.loads(item["events"]) if item["events"] else []
            result.append(item)
        return result

    def remove_webhook(self, webhook_id: int) -> bool:
        cur = self._execute("DELETE FROM webhooks WHERE id=?", (webhook_id,))
        return cur.rowcount > 0

    # Agent status & Rate Limit State
    def upsert_agent_status(
        self,
        agent: str,
        project_id: Optional[int],
        status: Optional[str],
        details: Optional[Dict[str, Any]],
        last_seen: Optional[int],
        rate_tokens: Optional[float],
        rate_refill_ts: Optional[int],
    ) -> None:
        row = self._query(
            "SELECT id FROM agent_status WHERE agent=? AND IFNULL(project_id,'')=IFNULL(?, '')",
            (agent, project_id),
        )
        details_json = json.dumps(details) if details is not None else None
        if row:
            sets = []
            params: List[Any] = []
            if status is not None:
                sets.append("status=?"); params.append(status)
            if details is not None:
                sets.append("details=?"); params.append(details_json)
            if last_seen is not None:
                sets.append("last_seen=?"); params.append(last_seen)
            if rate_tokens is not None:
                sets.append("rate_tokens=?"); params.append(rate_tokens)
            if rate_refill_ts is not None:
                sets.append("rate_refill_ts=?"); params.append(rate_refill_ts)
            if sets:
                params.extend([agent, project_id])
                self._execute(
                    f"UPDATE agent_status SET {', '.join(sets)} WHERE agent=? AND IFNULL(project_id,'')=IFNULL(?, '')",
                    tuple(params),
                )
        else:
            self._execute(
                "INSERT INTO agent_status(agent, project_id, status, details, last_seen, rate_tokens, rate_refill_ts) VALUES(?,?,?,?,?,?,?)",
                (agent, project_id, status, details_json, last_seen, rate_tokens, rate_refill_ts),
            )

    def get_agent_status(self, agent: str, project_id: Optional[int]) -> Optional[Dict[str, Any]]:
        rows = self._query(
            "SELECT * FROM agent_status WHERE agent=? AND IFNULL(project_id,'')=IFNULL(?, '')",
            (agent, project_id),
        )
        if not rows:
            return None
        r = dict(rows[0])
        if r.get("details"):
            try:
                r["details"] = json.loads(r["details"])  # type: ignore
            except Exception:
                pass
        return r

    # Floor control
    def take_floor(self, project_id: int, agent: str, ttl_seconds: int = 60) -> bool:
        now = int(time.time() * 1000)
        exp = now + ttl_seconds * 1000
        rows = self._query("SELECT holder_agent, expires_at FROM floors WHERE project_id=?", (project_id,))
        if rows:
            r = rows[0]
            if r["expires_at"] and r["expires_at"] > now and r["holder_agent"] != agent:
                return False
            self._execute("UPDATE floors SET holder_agent=?, expires_at=? WHERE project_id=?", (agent, exp, project_id))
        else:
            self._execute("INSERT INTO floors(project_id, holder_agent, expires_at) VALUES(?,?,?)", (project_id, agent, exp))
        return True

    def release_floor(self, project_id: int, agent: str) -> bool:
        rows = self._query("SELECT holder_agent FROM floors WHERE project_id=?", (project_id,))
        if not rows:
            return False
        if rows[0]["holder_agent"] != agent:
            return False
        self._execute("UPDATE floors SET holder_agent=NULL, expires_at=NULL WHERE project_id=?", (project_id,))
        return True

    def get_floor(self, project_id: int) -> Optional[Dict[str, Any]]:
        rows = self._query("SELECT * FROM floors WHERE project_id=?", (project_id,))
        if not rows:
            return None
        return dict(rows[0])

    # Digests
    def upsert_digest(self, project_id: int, content: str) -> None:
        ts = int(time.time() * 1000)
        rows = self._query("SELECT version FROM digests WHERE project_id=?", (project_id,))
        if rows:
            v = int(rows[0]["version"]) + 1
            self._execute("UPDATE digests SET version=?, content=?, updated_at=? WHERE project_id=?", (v, content, ts, project_id))
        else:
            self._execute("INSERT INTO digests(project_id, version, content, updated_at) VALUES(?,?,?,?)", (project_id, 1, content, ts))

    def get_digest(self, project_id: int) -> Optional[Dict[str, Any]]:
        rows = self._query("SELECT project_id, version, content, updated_at FROM digests WHERE project_id=?", (project_id,))
        if not rows:
            return None
        return dict(rows[0])

    # Docs
    def create_doc(self, title: str, source: Optional[str], project_id: Optional[int], version: int = 1) -> int:
        ts = int(time.time() * 1000)
        cur = self._execute(
            "INSERT INTO docs(project_id, title, source, version, created_at) VALUES(?,?,?,?,?)",
            (project_id, title, source, version, ts),
        )
        return int(cur.lastrowid)

    def add_doc_chunk(self, doc_id: int, chunk_index: int, text: str, sha256: str) -> int:
        ts = int(time.time() * 1000)
        cur = self._execute(
            "INSERT OR REPLACE INTO doc_chunks(doc_id, chunk_index, text, sha256, created_at) VALUES(?,?,?,?,?)",
            (doc_id, chunk_index, text, sha256, ts),
        )
        # Insert into FTS
        self._execute(
            "INSERT INTO docs_fts(rowid, content, doc_id, chunk_index) VALUES(?, ?, ?, ?)",
            (cur.lastrowid, text, doc_id, chunk_index),
        )
        return int(cur.lastrowid)

    def list_docs(self, project_id: Optional[int], limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        if project_id is None:
            rows = self._query(
                "SELECT id, project_id, title, source, version, created_at FROM docs ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset),
            )
        else:
            rows = self._query(
                "SELECT id, project_id, title, source, version, created_at FROM docs WHERE project_id=? ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (project_id, limit, offset),
            )
        return [dict(r) for r in rows]

    def list_doc_versions(self, title: str) -> List[Dict[str, Any]]:
        rows = self._query("SELECT id, title, version, created_at FROM docs WHERE title=? ORDER BY version DESC", (title,))
        return [dict(r) for r in rows]

    def get_doc_chunk(self, doc_id: int, chunk_index: int) -> Optional[Dict[str, Any]]:
        rows = self._query(
            "SELECT doc_id, chunk_index, text, sha256, created_at FROM doc_chunks WHERE doc_id=? AND chunk_index=?",
            (doc_id, chunk_index),
        )
        if not rows:
            return None
        return dict(rows[0])

    def search_docs(self, query: str, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        rows = self._query(
            "SELECT d.id as doc_id, d.title as title, c.chunk_index as chunk_index, c.text as text FROM docs_fts f JOIN doc_chunks c ON f.rowid=c.id JOIN docs d ON c.doc_id=d.id WHERE docs_fts MATCH ? LIMIT ? OFFSET ?",
            (query, limit, offset),
        )
        return [dict(r) for r in rows]
