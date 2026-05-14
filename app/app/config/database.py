"""
PostgreSQL-backed document store (JSONB + SQL queries).

Collections available:
    users, products, orders, invoices
"""

import json
import uuid
from typing import Any

import psycopg
from psycopg.rows import dict_row

from app.app.config.settings import get_settings


settings = get_settings()
_COLLECTIONS = ("users", "products", "orders", "invoices")
_conn: psycopg.Connection | None = None


def _validate_collection(collection: str) -> str:
    if collection not in _COLLECTIONS:
        raise ValueError(f"Unsupported collection: {collection}")
    return collection


def _get_conn() -> psycopg.Connection:
    global _conn
    if _conn is None or _conn.closed:
        _conn = psycopg.connect(settings.database_url)
        _conn.autocommit = True
    return _conn


def _ensure_schema() -> None:
    conn = _get_conn()
    with conn.cursor() as cur:
        for collection in _COLLECTIONS:
            cur.execute(
                f"CREATE TABLE IF NOT EXISTS {collection} ("
                "id TEXT PRIMARY KEY, "
                "doc JSONB NOT NULL"
                ")"
            )
            cur.execute(
                f"CREATE INDEX IF NOT EXISTS idx_{collection}_doc_gin "
                f"ON {collection} USING GIN (doc)"
            )
            cur.execute(
                f"CREATE INDEX IF NOT EXISTS idx_{collection}_created_at "
                f"ON {collection} ((doc->>'created_at'))"
            )


def _build_filter_payload(filters: dict[str, Any]) -> str:
    return json.dumps(filters, ensure_ascii=True)


async def connect_db() -> None:
    _ensure_schema()
    print("PostgreSQL document database ready")


async def close_db() -> None:
    global _conn
    if _conn is not None and not _conn.closed:
        _conn.close()
    _conn = None
    print("PostgreSQL document database closed")


def get_db():
    """Keep compatibility with Depends() signatures in controllers."""
    return _get_conn()


def new_id() -> str:
    return uuid.uuid4().hex


def db_insert(collection: str, doc: dict) -> str:
    table = _validate_collection(collection)
    conn = _get_conn()
    doc_id = doc.get("id") or new_id()
    payload = {**doc, "id": doc_id}

    with conn.cursor() as cur:
        cur.execute(
            f"INSERT INTO {table} (id, doc) VALUES (%s, %s::jsonb) "
            "ON CONFLICT (id) DO UPDATE SET doc = EXCLUDED.doc",
            (doc_id, json.dumps(payload, ensure_ascii=True)),
        )
    doc["id"] = doc_id
    return doc_id


def db_find_one(collection: str, **filters) -> dict | None:
    table = _validate_collection(collection)
    conn = _get_conn()
    payload = _build_filter_payload(filters)

    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            f"SELECT doc FROM {table} WHERE doc @> %s::jsonb LIMIT 1",
            (payload,),
        )
        row = cur.fetchone()
    if not row:
        return None
    return dict(row["doc"])


def db_find_all(collection: str, **filters) -> list[dict]:
    table = _validate_collection(collection)
    conn = _get_conn()
    payload = _build_filter_payload(filters)

    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            f"SELECT doc FROM {table} "
            "WHERE doc @> %s::jsonb "
            "ORDER BY COALESCE(doc->>'created_at', '') DESC",
            (payload,),
        )
        rows = cur.fetchall()
    return [dict(row["doc"]) for row in rows]


def db_update(collection: str, doc_id: str, updates: dict) -> dict | None:
    table = _validate_collection(collection)
    conn = _get_conn()

    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            f"UPDATE {table} "
            "SET doc = doc || %s::jsonb "
            "WHERE id = %s "
            "RETURNING doc",
            (json.dumps(updates, ensure_ascii=True), doc_id),
        )
        row = cur.fetchone()
    if not row:
        return None
    return dict(row["doc"])


def db_count(collection: str, **filters) -> int:
    table = _validate_collection(collection)
    conn = _get_conn()
    payload = _build_filter_payload(filters)

    with conn.cursor() as cur:
        cur.execute(
            f"SELECT COUNT(*) FROM {table} WHERE doc @> %s::jsonb",
            (payload,),
        )
        return int(cur.fetchone()[0])


def db_clear_all() -> None:
    """Wipe all collections. Used between tests."""
    conn = _get_conn()
    with conn.cursor() as cur:
        for col in _COLLECTIONS:
            cur.execute(f"DELETE FROM {col}")
