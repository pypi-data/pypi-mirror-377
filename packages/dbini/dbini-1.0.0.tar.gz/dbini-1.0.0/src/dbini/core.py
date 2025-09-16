# src/dbini/core.py
"""
dbini core storage engine
- Filesystem-backed collections: data/collections/<collection>/<docId>.json
- Files stored in data/files/<fileId>.<ext>
- Per-collection SQLite indexes using JSON1 (json_extract)
- WAL with HMAC chain to detect tampering
- Atomic writes with fsync and os.replace
- Advanced query operators: $eq, $ne, $gt, $gte, $lt, $lte, $in, $nin, $like, $size, $elemMatch, $exists, $regex
- Logical operators: $and, $or, $not
- Array operations and nested document querying
- Aggregations: count, min, max, avg, distinct, group_by, sum
- Upsert operations
- Full-text search capabilities
"""

from __future__ import annotations
import os
import json
import uuid
import tempfile
import shutil
import sqlite3
import threading
import hmac
import hashlib
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union
from collections import defaultdict

# ---------- Helpers ----------
def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def atomic_write_bytes(path: Path, data: bytes, mode: int = 0o600):
    """
    Atomically write bytes to path: write to tmp file, fsync, then os.replace.
    """
    ensure_dir(path.parent)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent))
    try:
        try:
            os.fchmod(fd, mode)
        except Exception:
            pass
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, str(path))
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except Exception:
                pass

def hmac_hex(key: bytes, msg: bytes) -> str:
    return hmac.new(key, msg, hashlib.sha256).hexdigest()

def read_json_file(path: Path) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_json_file(path: Path, obj: Any):
    atomic_write_bytes(path, json.dumps(obj, ensure_ascii=False, indent=2).encode("utf-8"))

def get_nested_value(doc: Dict[str, Any], path: str) -> Any:
    """Get nested value from document using dot notation (e.g., 'user.profile.age')"""
    keys = path.split('.')
    current = doc
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        elif isinstance(current, list) and key.isdigit():
            idx = int(key)
            if 0 <= idx < len(current):
                current = current[idx]
            else:
                return None
        else:
            return None
    return current

def set_nested_value(doc: Dict[str, Any], path: str, value: Any):
    """Set nested value in document using dot notation"""
    keys = path.split('.')
    current = doc
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    current[keys[-1]] = value

# ---------- Core DBini ----------
class DBini:
    def __init__(self, project_path: Union[str, Path], *, master_key: Optional[bytes] = None):
        """
        Initialize a project storage root.
        If master_key is not provided, a random key is generated and stored in meta/keys.json (HMAC key).
        """
        self.root = Path(project_path).resolve()
        self.meta = self.root / "meta"
        self.data = self.root / "data"
        self.collections_path = self.data / "collections"
        self.files_path = self.data / "files"
        self.index_path = self.root / "index"
        self.wal_path = self.root / "wal"
        ensure_dir(self.meta)
        ensure_dir(self.collections_path)
        ensure_dir(self.files_path)
        ensure_dir(self.index_path)
        ensure_dir(self.wal_path)

        self._lock = threading.RLock()
        self._conn_cache: Dict[str, sqlite3.Connection] = {}
        self._wal_file = self.wal_path / "append.log"
        self._keys_file = self.meta / "keys.json"
        self._load_or_create_keys(master_key)

    # ---------- Keys & HMAC ----------
    def _load_or_create_keys(self, master_key: Optional[bytes]):
        if self._keys_file.exists():
            try:
                data = read_json_file(self._keys_file)
                self._hmac_key = bytes.fromhex(data["hmac_key"])
            except Exception:
                # regen if corrupted
                self._hmac_key = master_key or hashlib.sha256(uuid.uuid4().bytes).digest()
                write_json_file(self._keys_file, {"hmac_key": self._hmac_key.hex()})
        else:
            self._hmac_key = master_key or hashlib.sha256(uuid.uuid4().bytes).digest()
            write_json_file(self._keys_file, {"hmac_key": self._hmac_key.hex()})

    # ---------- WAL ----------
    def append_wal(self, entry: Dict[str, Any]):
        """
        Append a JSONL entry to wal/append.log with HMAC chaining:
        Each line: JSON object with appended field "_hmac" which signs (prev_hmac + line_bytes)
        """
        with self._lock:
            prev_hmac = None
            if self._wal_file.exists():
                # read last line's hmac
                try:
                    with open(self._wal_file, "rb") as f:
                        f.seek(0, os.SEEK_END)
                        sz = f.tell()
                        if sz == 0:
                            prev_hmac = None
                        else:
                            chunk = min(4096, sz)
                            f.seek(sz - chunk)
                            buf = f.read(chunk)
                            last_line = buf.splitlines()[-1]
                            last_json = json.loads(last_line.decode("utf-8"))
                            prev_hmac = last_json.get("_hmac")
                except Exception:
                    prev_hmac = None
            entry_copy = dict(entry)
            entry_copy["_ts"] = utcnow_iso()
            message = json.dumps({k: v for k, v in entry_copy.items() if k != "_hmac"}, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
            h = hmac.new(self._hmac_key, (str(prev_hmac or "")).encode("utf-8") + message, hashlib.sha256).hexdigest()
            entry_copy["_hmac"] = h
            line = json.dumps(entry_copy, ensure_ascii=False).encode("utf-8") + b"\n"
            # atomic append: open in ab and fsync
            with open(self._wal_file, "ab") as f:
                f.write(line)
                f.flush()
                os.fsync(f.fileno())

    def verify_wal(self) -> Tuple[bool, Optional[int], Optional[str]]:
        """
        Verify WAL chain. Returns (is_valid, bad_line_number_or_None, message_or_None)
        """
        if not self._wal_file.exists():
            return True, None, None
        prev_hmac = None
        with open(self._wal_file, "rb") as f:
            for i, raw in enumerate(f, start=1):
                try:
                    obj = json.loads(raw.decode("utf-8"))
                except Exception as e:
                    return False, i, f"bad json: {e}"
                h = obj.get("_hmac")
                check_msg = json.dumps({k: v for k, v in obj.items() if k != "_hmac"}, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
                expected = hmac.new(self._hmac_key, (str(prev_hmac or "")).encode("utf-8") + check_msg, hashlib.sha256).hexdigest()
                if expected != h:
                    return False, i, "hmac mismatch"
                prev_hmac = h
        return True, None, None

    # ---------- SQLite index helpers ----------
    def _get_index_conn(self, collection: str) -> sqlite3.Connection:
        """
        Each collection has its own sqlite file under index/<collection>.sqlite
        Schema:
          - docs(id TEXT PRIMARY KEY, json TEXT)
        We use JSON1 functions to index fields when requested.
        """
        with self._lock:
            if collection in self._conn_cache:
                return self._conn_cache[collection]
            dbfile = self.index_path / f"{collection}.sqlite"
            conn = sqlite3.connect(str(dbfile), check_same_thread=False)
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("CREATE TABLE IF NOT EXISTS docs (id TEXT PRIMARY KEY, json TEXT NOT NULL);")
            # Enable FTS5 for full-text search
            conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS docs_fts USING fts5(id, content, tokenize='unicode61');")
            conn.commit()
            self._conn_cache[collection] = conn
            return conn

    def ensure_index_on(self, collection: str, json_path: str):
        """
        Create an index on json_extract(json, '$.json_path')
        json_path: dot-separated path like 'profile.age' -> json_extract(json, '$.profile.age')
        """
        col = collection
        col_index = json_path.replace(".", "_")
        idx_name = f"idx_{col}_{col_index}"
        conn = self._get_index_conn(col)
        with conn:
            expr = f"json_extract(json, '$.{json_path}')"
            conn.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON docs ({expr});")

    def _index_upsert(self, collection: str, doc_id: str, doc: Dict[str, Any]):
        conn = self._get_index_conn(collection)
        with conn:
            json_str = json.dumps(doc, ensure_ascii=False)
            conn.execute(
                "INSERT INTO docs (id, json) VALUES (?, ?) ON CONFLICT(id) DO UPDATE SET json=excluded.json;",
                (doc_id, json_str),
            )
            # Update FTS index with searchable content
            content = self._extract_searchable_content(doc)
            conn.execute(
                "INSERT INTO docs_fts (id, content) VALUES (?, ?) ON CONFLICT(id) DO UPDATE SET content=excluded.content;",
                (doc_id, content)
            )

    def _extract_searchable_content(self, doc: Dict[str, Any]) -> str:
        """Extract searchable text content from a document"""
        def extract_text(obj):
            if isinstance(obj, str):
                return obj
            elif isinstance(obj, dict):
                return ' '.join(extract_text(v) for v in obj.values())
            elif isinstance(obj, list):
                return ' '.join(extract_text(item) for item in obj)
            else:
                return str(obj)
        
        return extract_text(doc)

    def _index_delete(self, collection: str, doc_id: str):
        conn = self._get_index_conn(collection)
        with conn:
            conn.execute("DELETE FROM docs WHERE id = ?;", (doc_id,))
            conn.execute("DELETE FROM docs_fts WHERE id = ?;", (doc_id,))

    def query_index(self, collection: str, where_sql: str, params: Tuple[Any, ...] = (), limit: Optional[int] = None) -> List[str]:
        """
        Query index for matching doc ids. `where_sql` is a SQL WHERE clause using json_extract, e.g.
          "json_extract(json, '$.age') >= ? AND json_extract(json, '$.active') = 1"
        Returns list of doc ids.
        """
        conn = self._get_index_conn(collection)
        q = "SELECT id FROM docs WHERE " + where_sql
        if limit:
            q += f" LIMIT {int(limit)}"
        cur = conn.execute(q, params)
        return [row[0] for row in cur.fetchall()]

    def text_search(self, collection: str, search_text: str, limit: Optional[int] = None) -> List[str]:
        """Full-text search using FTS5"""
        conn = self._get_index_conn(collection)
        q = "SELECT id FROM docs_fts WHERE docs_fts MATCH ?"
        if limit:
            q += f" LIMIT {int(limit)}"
        cur = conn.execute(q, (search_text,))
        return [row[0] for row in cur.fetchall()]

    # ---------- Document operations ----------
    def _doc_path(self, collection: str, doc_id: str) -> Path:
        return self.collections_path / collection / f"{doc_id}.json"

    def add_document(self, collection: str, doc: Dict[str, Any], doc_id: Optional[str] = None) -> str:
        """
        Add a new document: assigns an id if not provided, adds created_at/updated_at, writes file atomically,
        updates index and WAL.
        """
        with self._lock:
            if doc_id is None:
                doc_id = uuid.uuid4().hex
            now = utcnow_iso()
            doc.setdefault("created_at", now)
            doc["updated_at"] = now
            # ensure collection dir
            col_dir = self.collections_path / collection
            ensure_dir(col_dir)
            path = self._doc_path(collection, doc_id)
            write_json_file(path, doc)
            # index
            try:
                self._index_upsert(collection, doc_id, doc)
            except Exception:
                pass
            # wal
            try:
                self.append_wal({"op": "put", "collection": collection, "id": doc_id})
            except Exception:
                pass
            return doc_id

    def get_document(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        path = self._doc_path(collection, doc_id)
        if not path.exists():
            return None
        try:
            return read_json_file(path)
        except Exception:
            return None

    def update_document(self, collection: str, doc_id: str, updates: Dict[str, Any]) -> bool:
        with self._lock:
            path = self._doc_path(collection, doc_id)
            if not path.exists():
                return False
            doc = read_json_file(path)
            doc.update(updates)
            doc["updated_at"] = utcnow_iso()
            write_json_file(path, doc)
            try:
                self._index_upsert(collection, doc_id, doc)
            except Exception:
                pass
            try:
                self.append_wal({"op": "patch", "collection": collection, "id": doc_id, "fields": list(updates.keys())})
            except Exception:
                pass
            return True

    def upsert_document(self, collection: str, filters: Dict[str, Any], updates: Dict[str, Any], doc_id: Optional[str] = None) -> Tuple[str, bool]:
        """
        Update document if it exists (matching filters), otherwise insert.
        Returns (doc_id, was_inserted)
        """
        with self._lock:
            # Try to find existing document
            existing_docs = self.find(collection, filters=filters, limit=1)
            
            if existing_docs:
                # Update existing
                existing_doc = existing_docs[0]
                existing_id = None
                # Find the doc_id by checking all docs (inefficient but works)
                col_dir = self.collections_path / collection
                if col_dir.exists():
                    for p in col_dir.glob("*.json"):
                        try:
                            candidate = read_json_file(p)
                            if candidate == existing_doc:
                                existing_id = p.stem
                                break
                        except Exception:
                            continue
                
                if existing_id:
                    self.update_document(collection, existing_id, updates)
                    return existing_id, False
            
            # Insert new document
            new_doc = dict(updates)
            new_doc.update(filters)  # Include filter criteria in new doc
            new_id = self.add_document(collection, new_doc, doc_id=doc_id)
            return new_id, True

    def delete_document(self, collection: str, doc_id: str) -> bool:
        with self._lock:
            path = self._doc_path(collection, doc_id)
            if not path.exists():
                return False
            try:
                path.unlink()
            except Exception:
                return False
            try:
                self._index_delete(collection, doc_id)
            except Exception:
                pass
            try:
                self.append_wal({"op": "del", "collection": collection, "id": doc_id})
            except Exception:
                pass
            return True

    # ---------- Advanced Querying ----------
    def find(
        self,
        collection: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        sort: Optional[List[Tuple[str, int]]] = None,
        search: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        High-level query over a collection.
        Supported operators in filter values: $eq (default), $ne, $gt, $gte, $lt, $lte, $in, $nin, $like, $size, $elemMatch, $exists, $regex
        Logical operators (at top-level of filters): $and, $or, $not
        Array operations: $size for array length, $elemMatch for array element matching
        search: full-text search query
        """
        # Full-text search takes precedence
        if search:
            ids = self.text_search(collection, search, limit)
            results = []
            for id_ in ids:
                doc = self.get_document(collection, id_)
                if doc is not None:
                    results.append(doc)
            if sort:
                results = self._apply_sort(results, sort)
            return results[:limit] if limit else results

        # No filters => return all docs (fast path)
        if not filters:
            col_dir = self.collections_path / collection
            if not col_dir.exists():
                return []
            docs = []
            for p in sorted(col_dir.glob("*.json")):
                try:
                    docs.append(read_json_file(p))
                except Exception:
                    continue
            if sort:
                docs = self._apply_sort(docs, sort)
            return docs[:limit] if limit else docs

        # Use in-memory filtering for complex operations not supported by SQLite
        if self._requires_memory_filtering(filters):
            return self._memory_filter(collection, filters, limit, sort)

        # Use SQLite index for simple queries
        where_sql, params = self._build_where(filters)
        if not where_sql:
            return []  # no valid where clause built
        ids = self.query_index(collection, where_sql, tuple(params), limit=limit)
        results: List[Dict[str, Any]] = []
        for id_ in ids:
            doc = self.get_document(collection, id_)
            if doc is not None:
                results.append(doc)
        if sort:
            results = self._apply_sort(results, sort)
        return results[:limit] if limit else results

    def _requires_memory_filtering(self, filters: Dict[str, Any]) -> bool:
        """Check if filters require in-memory processing (contains $size, $elemMatch, etc.)"""
        def check_condition(cond):
            if isinstance(cond, dict):
                for op in cond.keys():
                    if op in ['$size', '$elemMatch', '$regex']:
                        return True
                    if op in ['$and', '$or'] and isinstance(cond[op], list):
                        for sub_cond in cond[op]:
                            if check_condition(sub_cond):
                                return True
            return False
        
        return check_condition(filters)

    def _memory_filter(self, collection: str, filters: Dict[str, Any], limit: Optional[int], sort: Optional[List[Tuple[str, int]]]) -> List[Dict[str, Any]]:
        """Filter documents in memory for complex operations"""
        col_dir = self.collections_path / collection
        if not col_dir.exists():
            return []
        
        docs = []
        for p in col_dir.glob("*.json"):
            try:
                doc = read_json_file(p)
                if self._match_document(doc, filters):
                    docs.append(doc)
                    if limit and len(docs) >= limit:
                        break
            except Exception:
                continue
        
        if sort:
            docs = self._apply_sort(docs, sort)
        
        return docs[:limit] if limit else docs

    def _match_document(self, doc: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if document matches filters (supports all operators including array ops)"""
        def evaluate_condition(field_path: str, condition: Any) -> bool:
            value = get_nested_value(doc, field_path)
            
            if isinstance(condition, dict):
                for op, expected in condition.items():
                    if op == "$eq":
                        if value != expected:
                            return False
                    elif op == "$ne":
                        if value == expected:
                            return False
                    elif op == "$gt":
                        if not (value is not None and value > expected):
                            return False
                    elif op == "$gte":
                        if not (value is not None and value >= expected):
                            return False
                    elif op == "$lt":
                        if not (value is not None and value < expected):
                            return False
                    elif op == "$lte":
                        if not (value is not None and value <= expected):
                            return False
                    elif op == "$in":
                        if value not in expected:
                            return False
                    elif op == "$nin":
                        if value in expected:
                            return False
                    elif op == "$like":
                        if not (isinstance(value, str) and expected.lower() in value.lower()):
                            return False
                    elif op == "$regex":
                        if not (isinstance(value, str) and re.search(expected, value)):
                            return False
                    elif op == "$exists":
                        exists = value is not None
                        if exists != expected:
                            return False
                    elif op == "$size":
                        if not (isinstance(value, (list, str)) and len(value) == expected):
                            return False
                    elif op == "$elemMatch":
                        if not isinstance(value, list):
                            return False
                        found_match = False
                        for item in value:
                            if isinstance(item, dict) and self._match_document(item, expected):
                                found_match = True
                                break
                        if not found_match:
                            return False
                return True
            else:
                # Simple equality
                return value == condition

        # Handle logical operators
        if "$and" in filters:
            return all(self._match_document(doc, sub_filter) for sub_filter in filters["$and"])
        elif "$or" in filters:
            return any(self._match_document(doc, sub_filter) for sub_filter in filters["$or"])
        elif "$not" in filters:
            return not self._match_document(doc, filters["$not"])
        else:
            # Regular field conditions
            for field_path, condition in filters.items():
                if not evaluate_condition(field_path, condition):
                    return False
            return True

    def _build_where(self, filters: Dict[str, Any]) -> Tuple[str, List[Any]]:
        """
        Recursively build WHERE SQL for filters with support for $and / $or.
        Returns (where_sql, params).
        """
        params: List[Any] = []
        clauses: List[str] = []

        def handle_key_expr(key: str, cond: Any) -> Tuple[str, List[Any]]:
            path_expr = f"json_extract(json, '$.{key}')"
            local_params: List[Any] = []
            if isinstance(cond, dict):
                sub_clauses: List[str] = []
                for op, val in cond.items():
                    if op == "$eq":
                        sub_clauses.append(f"{path_expr} = ?"); local_params.append(val)
                    elif op == "$ne":
                        sub_clauses.append(f"{path_expr} != ?"); local_params.append(val)
                    elif op == "$gt":
                        sub_clauses.append(f"{path_expr} > ?"); local_params.append(val)
                    elif op == "$gte":
                        sub_clauses.append(f"{path_expr} >= ?"); local_params.append(val)
                    elif op == "$lt":
                        sub_clauses.append(f"{path_expr} < ?"); local_params.append(val)
                    elif op == "$lte":
                        sub_clauses.append(f"{path_expr} <= ?"); local_params.append(val)
                    elif op == "$in":
                        if not isinstance(val, (list, tuple)) or len(val) == 0:
                            raise ValueError("$in requires a non-empty list")
                        placeholders = ",".join(["?"] * len(val))
                        sub_clauses.append(f"{path_expr} IN ({placeholders})")
                        local_params.extend(val)
                    elif op == "$nin":
                        if not isinstance(val, (list, tuple)) or len(val) == 0:
                            raise ValueError("$nin requires a non-empty list")
                        placeholders = ",".join(["?"] * len(val))
                        sub_clauses.append(f"{path_expr} NOT IN ({placeholders})")
                        local_params.extend(val)
                    elif op == "$like":
                        sub_clauses.append(f"{path_expr} LIKE ?"); local_params.append(val)
                    elif op == "$exists":
                        if val:
                            sub_clauses.append(f"{path_expr} IS NOT NULL")
                        else:
                            sub_clauses.append(f"{path_expr} IS NULL")
                    else:
                        # For complex operators, return empty to force memory filtering
                        return "", []
                return " AND ".join(sub_clauses), local_params
            else:
                # equality shorthand
                return f"{path_expr} = ?", [cond]

        # Logical operators at this level
        if "$and" in filters:
            if not isinstance(filters["$and"], list):
                raise ValueError("$and must be a list")
            sub_clauses: List[str] = []
            for sub in filters["$and"]:
                sub_sql, sub_params = self._build_where(sub)
                if sub_sql:
                    sub_clauses.append(f"({sub_sql})")
                    params.extend(sub_params)
            clauses.append(" AND ".join(sub_clauses))
        elif "$or" in filters:
            if not isinstance(filters["$or"], list):
                raise ValueError("$or must be a list")
            sub_clauses: List[str] = []
            for sub in filters["$or"]:
                sub_sql, sub_params = self._build_where(sub)
                if sub_sql:
                    sub_clauses.append(f"({sub_sql})")
                    params.extend(sub_params)
            clauses.append(" OR ".join(sub_clauses))
        else:
            # simple key -> condition mappings
            for key, cond in filters.items():
                sql_fragment, local_params = handle_key_expr(key, cond)
                if sql_fragment:  # Only add if we got valid SQL
                    clauses.append(sql_fragment)
                    params.extend(local_params)

        where_sql = " AND ".join([c for c in clauses if c])
        return where_sql, params

    def _apply_sort(self, docs: List[Dict[str, Any]], sort: List[Tuple[str, int]]) -> List[Dict[str, Any]]:
        # stable multi-key sort: apply in reverse
        for key, direction in reversed(sort):
            docs.sort(key=lambda d: get_nested_value(d, key) or 0, reverse=(direction < 0))
        return docs

    # ---------- Enhanced Aggregations ----------
    def aggregate(self, collection: str, op: str, field: Optional[str] = None, group_by: Optional[str] = None) -> Any:
        """
        Enhanced aggregation functions: count, min, max, avg, distinct, sum, group_by
        - For count, field may be None.
        - For distinct, returns list of distinct values.
        - For group_by, groups results by the specified field.
        """
        conn = self._get_index_conn(collection)
        
        if op == "count":
            if group_by:
                expr = f"json_extract(json, '$.{group_by}')"
                q = f"SELECT {expr}, COUNT(*) FROM docs GROUP BY {expr}"
                cur = conn.execute(q)
                return {str(row[0]): row[1] for row in cur.fetchall()}
            else:
                q = "SELECT COUNT(*) FROM docs"
                cur = conn.execute(q)
                return cur.fetchone()[0]
        
        if not field:
            raise ValueError("field is required for this aggregation")
        
        expr = f"json_extract(json, '$.{field}')"
        
        if group_by:
            group_expr = f"json_extract(json, '$.{group_by}')"
            if op == "min":
                q = f"SELECT {group_expr}, MIN({expr}) FROM docs GROUP BY {group_expr}"
            elif op == "max":
                q = f"SELECT {group_expr}, MAX({expr}) FROM docs GROUP BY {group_expr}"
            elif op == "avg":
                q = f"SELECT {group_expr}, AVG({expr}) FROM docs GROUP BY {group_expr}"
            elif op == "sum":
                q = f"SELECT {group_expr}, SUM({expr}) FROM docs GROUP BY {group_expr}"
            else:
                raise ValueError(f"Unsupported grouped aggregation: {op}")
            
            cur = conn.execute(q)
            return {str(row[0]): row[1] for row in cur.fetchall()}
        else:
            if op == "min":
                q = f"SELECT MIN({expr}) FROM docs"
                cur = conn.execute(q)
                return cur.fetchone()[0]
            elif op == "max":
                q = f"SELECT MAX({expr}) FROM docs"
                cur = conn.execute(q)
                return cur.fetchone()[0]
            elif op == "avg":
                q = f"SELECT AVG({expr}) FROM docs"
                cur = conn.execute(q)
                return cur.fetchone()[0]
            elif op == "sum":
                q = f"SELECT SUM({expr}) FROM docs"
                cur = conn.execute(q)
                return cur.fetchone()[0]
            elif op == "distinct":
                q = f"SELECT DISTINCT {expr} FROM docs"
                cur = conn.execute(q)
                return [r[0] for r in cur.fetchall()]
            else:
                raise ValueError(f"Unsupported aggregation: {op}")

    # ---------- Bulk Operations ----------
    def bulk_insert(self, collection: str, docs: List[Dict[str, Any]]) -> List[str]:
        """Insert multiple documents in a single operation"""
        doc_ids = []
        with self._lock:
            for doc in docs:
                doc_id = self.add_document(collection, doc)
                doc_ids.append(doc_id)
        return doc_ids

    def bulk_update(self, collection: str, filters: Dict[str, Any], updates: Dict[str, Any]) -> int:
        """Update multiple documents matching filters"""
        matching_docs = self.find(collection, filters=filters)
        count = 0
        
        # Get doc IDs for matching documents
        col_dir = self.collections_path / collection
        if not col_dir.exists():
            return 0
            
        with self._lock:
            for p in col_dir.glob("*.json"):
                try:
                    doc = read_json_file(p)
                    if self._match_document(doc, filters):
                        doc_id = p.stem
                        if self.update_document(collection, doc_id, updates):
                            count += 1
                except Exception:
                    continue
        
        return count

    def bulk_delete(self, collection: str, filters: Dict[str, Any]) -> int:
        """Delete multiple documents matching filters"""
        col_dir = self.collections_path / collection
        if not col_dir.exists():
            return 0
            
        count = 0
        with self._lock:
            for p in col_dir.glob("*.json"):
                try:
                    doc = read_json_file(p)
                    if self._match_document(doc, filters):
                        doc_id = p.stem
                        if self.delete_document(collection, doc_id):
                            count += 1
                except Exception:
                    continue
        
        return count

    # ---------- File operations ----------
    def save_file(self, src_path: Union[str, Path], *, dest_filename: Optional[str] = None) -> str:
        """
        Save an arbitrary file under data/files/ with uuid prefix. Returns file_id (uuid hex).
        The actual filename on disk is <file_id>_<safe_name.ext>
        """
        src = Path(src_path)
        if not src.exists():
            raise FileNotFoundError(src)
        file_id = uuid.uuid4().hex
        safe_name = src.name.replace(" ", "_")
        if dest_filename:
            safe_name = dest_filename
        dest_name = f"{file_id}_{safe_name}"
        dest = self.files_path / dest_name
        # atomic copy via temp
        ensure_dir(self.files_path)
        with open(src, "rb") as fsrc:
            data = fsrc.read()
        atomic_write_bytes(dest, data)
        # update files index sqlite
        fi = self.index_path / "files.index.sqlite"
        conn = sqlite3.connect(str(fi))
        with conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS files (id TEXT PRIMARY KEY, name TEXT, size INTEGER, sha256 TEXT, created_at TEXT);"
            )
            sha = hashlib.sha256(data).hexdigest()
            conn.execute(
                "INSERT INTO files (id, name, size, sha256, created_at) VALUES (?, ?, ?, ?, ?) ON CONFLICT(id) DO NOTHING;",
                (file_id, dest_name, len(data), sha, utcnow_iso()),
            )
        conn.close()
        # wal
        try:
            self.append_wal({"op": "file_put", "file_id": file_id, "name": dest_name})
        except Exception:
            pass
        return file_id

    def get_file_path(self, file_id: str) -> Optional[str]:
        """
        Return absolute path of a saved file by searching for files starting with <file_id>_.
        """
        for p in self.files_path.glob(f"{file_id}_*"):
            return str(p.resolve())
        # fallback to sqlite lookup
        fi = self.index_path / "files.index.sqlite"
        if fi.exists():
            conn = sqlite3.connect(str(fi))
            try:
                cur = conn.execute("SELECT name FROM files WHERE id = ? LIMIT 1;", (file_id,))
                row = cur.fetchone()
                if row:
                    name = row[0]
                    p = self.files_path / name
                    if p.exists():
                        return str(p.resolve())
            finally:
                conn.close()
        return None

    def list_files(self) -> List[Dict[str, Any]]:
        fi = self.index_path / "files.index.sqlite"
        if not fi.exists():
            return []
        conn = sqlite3.connect(str(fi))
        try:
            cur = conn.execute("SELECT id, name, size, sha256, created_at FROM files ORDER BY created_at DESC;")
            return [{"id": r[0], "name": r[1], "size": r[2], "sha256": r[3], "created_at": r[4]} for r in cur.fetchall()]
        finally:
            conn.close()

    # ---------- Schema Validation ----------
    def set_schema(self, collection: str, schema: Dict[str, Any]):
        """Set validation schema for a collection"""
        schema_file = self.meta / f"{collection}_schema.json"
        write_json_file(schema_file, schema)

    def get_schema(self, collection: str) -> Optional[Dict[str, Any]]:
        """Get validation schema for a collection"""
        schema_file = self.meta / f"{collection}_schema.json"
        if schema_file.exists():
            return read_json_file(schema_file)
        return None

    def validate_document(self, collection: str, doc: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate document against collection schema. Returns (is_valid, errors)"""
        schema = self.get_schema(collection)
        if not schema:
            return True, []  # No schema means valid
        
        errors = []
        
        def validate_field(field_name: str, value: Any, field_schema: Dict[str, Any]):
            # Type validation
            expected_type = field_schema.get("type")
            if expected_type:
                type_map = {
                    "string": str,
                    "number": (int, float),
                    "integer": int,
                    "boolean": bool,
                    "array": list,
                    "object": dict
                }
                expected_python_type = type_map.get(expected_type)
                if expected_python_type and not isinstance(value, expected_python_type):
                    errors.append(f"Field '{field_name}' should be {expected_type}, got {type(value).__name__}")
            
            # Required validation
            if field_schema.get("required", False) and value is None:
                errors.append(f"Field '{field_name}' is required")
            
            # Min/max validation for numbers
            if isinstance(value, (int, float)):
                if "min" in field_schema and value < field_schema["min"]:
                    errors.append(f"Field '{field_name}' should be >= {field_schema['min']}")
                if "max" in field_schema and value > field_schema["max"]:
                    errors.append(f"Field '{field_name}' should be <= {field_schema['max']}")
            
            # String length validation
            if isinstance(value, str):
                if "minLength" in field_schema and len(value) < field_schema["minLength"]:
                    errors.append(f"Field '{field_name}' should have at least {field_schema['minLength']} characters")
                if "maxLength" in field_schema and len(value) > field_schema["maxLength"]:
                    errors.append(f"Field '{field_name}' should have at most {field_schema['maxLength']} characters")
        
        # Validate fields
        for field_name, field_schema in schema.get("fields", {}).items():
            value = get_nested_value(doc, field_name)
            validate_field(field_name, value, field_schema)
        
        return len(errors) == 0, errors

    # ---------- Utilities ----------
    def list_collections(self) -> List[str]:
        if not self.collections_path.exists():
            return []
        return sorted([p.name for p in self.collections_path.iterdir() if p.is_dir()])

    def collection_stats(self, collection: str) -> Dict[str, Any]:
        """Get statistics for a collection"""
        conn = self._get_index_conn(collection)
        cur = conn.execute("SELECT COUNT(*) FROM docs")
        doc_count = cur.fetchone()[0]
        
        col_dir = self.collections_path / collection
        total_size = 0
        if col_dir.exists():
            for p in col_dir.glob("*.json"):
                try:
                    total_size += p.stat().st_size
                except Exception:
                    continue
        
        return {
            "document_count": doc_count,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }

    def export_snapshot(self, snapshot_dir: Union[str, Path]) -> str:
        """
        Export a point-in-time snapshot (copy project content) to snapshot_dir.
        Returns path to snapshot root.
        """
        snapshot_root = Path(snapshot_dir)
        ensure_dir(snapshot_root)
        dst = snapshot_root / self.root.name
        if dst.exists():
            raise FileExistsError(dst)
        shutil.copytree(self.root, dst)
        return str(dst.resolve())

    def restore_snapshot(self, snapshot_path: Union[str, Path]):
        """
        Restore a snapshot into the project root. WARNING: overwrites current data.
        """
        snap = Path(snapshot_path)
        if not snap.exists():
            raise FileNotFoundError(snap)
        tmp_old = self.root.with_suffix(".bak")
        if tmp_old.exists():
            shutil.rmtree(tmp_old)
        os.rename(self.root, tmp_old)
        try:
            shutil.copytree(snap, self.root)
        except Exception as e:
            # rollback
            if self.root.exists():
                shutil.rmtree(self.root)
            os.rename(tmp_old, self.root)
            raise e
        shutil.rmtree(tmp_old)
        with self._lock:
            for c in list(self._conn_cache.values()):
                try:
                    c.close()
                except Exception:
                    pass
            self._conn_cache.clear()

    # ---------- Close / cleanup ----------
    def close(self):
        with self._lock:
            for conn in self._conn_cache.values():
                try:
                    conn.close()
                except Exception:
                    pass
            self._conn_cache.clear()

# ---------- Enhanced Collection wrapper ----------
class Collection:
    def __init__(self, db: DBini, name: str):
        self.db = db
        self.name = name

    def add(self, doc: Dict[str, Any], doc_id: Optional[str] = None) -> str:
        return self.db.add_document(self.name, doc, doc_id=doc_id)

    def get(self, doc_id: str) -> Optional[Dict[str, Any]]:
        return self.db.get_document(self.name, doc_id)

    def update(self, doc_id: str, updates: Dict[str, Any]) -> bool:
        return self.db.update_document(self.name, doc_id, updates)
    
    def upsert(self, filters: Dict[str, Any], updates: Dict[str, Any], doc_id: Optional[str] = None) -> Tuple[str, bool]:
        return self.db.upsert_document(self.name, filters, updates, doc_id)

    def delete(self, doc_id: str) -> bool:
        return self.db.delete_document(self.name, doc_id)

    def find(self, filters: Optional[Dict[str, Any]] = None, limit: Optional[int] = None, 
             sort: Optional[List[Tuple[str, int]]] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
        return self.db.find(self.name, filters=filters, limit=limit, sort=sort, search=search)

    def find_one(self, filters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        results = self.find(filters, limit=1)
        return results[0] if results else None

    def aggregate(self, op: str, field: Optional[str] = None, group_by: Optional[str] = None) -> Any:
        return self.db.aggregate(self.name, op, field, group_by)
    
    def bulk_insert(self, docs: List[Dict[str, Any]]) -> List[str]:
        return self.db.bulk_insert(self.name, docs)
    
    def bulk_update(self, filters: Dict[str, Any], updates: Dict[str, Any]) -> int:
        return self.db.bulk_update(self.name, filters, updates)
    
    def bulk_delete(self, filters: Dict[str, Any]) -> int:
        return self.db.bulk_delete(self.name, filters)
    
    def create_index(self, field: str):
        return self.db.ensure_index_on(self.name, field)
    
    def set_schema(self, schema: Dict[str, Any]):
        return self.db.set_schema(self.name, schema)
    
    def get_schema(self) -> Optional[Dict[str, Any]]:
        return self.db.get_schema(self.name)
    
    def stats(self) -> Dict[str, Any]:
        return self.db.collection_stats(self.name)