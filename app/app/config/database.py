"""
SQLite-backed document store (NoSQL-style API)
==============================================
Persists collections as JSON documents inside SQLite tables.

Collections available:
    users, products, orders, invoices
"""

import json
import sqlite3
import uuid
from pathlib import Path
from typing import Any


_DB_FILE = Path(__file__).resolve().parents[2] / "data" / "bitmarket.db"
_COLLECTIONS = ("users", "products", "orders", "invoices")
_conn: sqlite3.Connection | None = None


def _get_conn() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _DB_FILE.parent.mkdir(parents=True, exist_ok=True)
        _conn = sqlite3.connect(_DB_FILE)
    return _conn


def _ensure_schema() -> None:
    conn = _get_conn()
    for collection in _COLLECTIONS:
        conn.execute(
            f"CREATE TABLE IF NOT EXISTS {collection} ("
            "id TEXT PRIMARY KEY, "
            "doc TEXT NOT NULL"
            ")"
        )
    conn.commit()


def _read_doc(row: sqlite3.Row | tuple | None) -> dict | None:
    if not row:
        return None
    if isinstance(row, sqlite3.Row):
        raw = row["doc"]
    else:
        raw = row[1]
    return json.loads(raw)


def _matches_filters(doc: dict, filters: dict[str, Any]) -> bool:
    return all(doc.get(k) == v for k, v in filters.items())


# ── Lifecycle (kept for API compatibility with main.py) ────

async def connect_db() -> None:
    conn = _get_conn()
    conn.row_factory = sqlite3.Row
    _ensure_schema()
    print(f"✅ SQLite document database ready: {_DB_FILE}")


async def close_db() -> None:
    global _conn
    if _conn is not None:
        _conn.close()
        _conn = None
    print("🔌 SQLite document database closed")


def get_db():
    """Keep compatibility with Depends() signatures in controllers."""
    return _get_conn()


# ── CRUD helpers ───────────────────────────────────────────

def new_id() -> str:
    """Generate a unique document ID."""
    return uuid.uuid4().hex


def db_insert(collection: str, doc: dict) -> str:
    """Insert a document and return its id."""
    conn = _get_conn()
    doc_id = doc.get("id") or new_id()
    doc["id"] = doc_id
    payload = {**doc, "id": doc_id}
    conn.execute(
        f"INSERT OR REPLACE INTO {collection} (id, doc) VALUES (?, ?)",
        (doc_id, json.dumps(payload, ensure_ascii=True)),
    )
    conn.commit()
    return doc_id


def db_find_one(collection: str, **filters) -> dict | None:
    """Return first document matching all keyword filters."""
    conn = _get_conn()
    rows = conn.execute(f"SELECT id, doc FROM {collection}").fetchall()
    for row in rows:
        doc = _read_doc(row)
        if doc and _matches_filters(doc, filters):
            return dict(doc)
    return None


def db_find_all(collection: str, **filters) -> list[dict]:
    """Return all documents matching all keyword filters."""
    conn = _get_conn()
    rows = conn.execute(f"SELECT id, doc FROM {collection}").fetchall()
    results = []
    for row in rows:
        doc = _read_doc(row)
        if doc and _matches_filters(doc, filters):
            results.append(dict(doc))
    return sorted(results, key=lambda d: d.get("created_at", ""), reverse=True)


def db_update(collection: str, doc_id: str, updates: dict) -> dict | None:
    """Update fields on a document by id. Returns updated doc or None."""
    conn = _get_conn()
    row = conn.execute(
        f"SELECT id, doc FROM {collection} WHERE id = ?",
        (doc_id,),
    ).fetchone()
    current = _read_doc(row)
    if not current:
        return None
    current.update(updates)
    conn.execute(
        f"UPDATE {collection} SET doc = ? WHERE id = ?",
        (json.dumps(current, ensure_ascii=True), doc_id),
    )
    conn.commit()
    return dict(current)


def db_count(collection: str, **filters) -> int:
    return len(db_find_all(collection, **filters))


def db_clear_all() -> None:
    """Wipe all collections. Used between tests."""
    conn = _get_conn()
    for col in _COLLECTIONS:
        conn.execute(f"DELETE FROM {col}")
    conn.commit()
