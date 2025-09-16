# src/dbini/server.py
"""
Enhanced DBini REST + WebSocket server.

Features:
- CRUD endpoints for documents with upsert support
- Advanced query endpoint with array operations and full-text search
- Bulk operations (insert, update, delete)
- File upload / download
- Schema validation endpoints
- Collection statistics
- List collections & files
- WebSocket realtime: tails wal/append.log and pushes new WAL entries to subscribers
- Enhanced error handling and validation

Usage:
    from dbini.server import serve
    serve(project_root="myproject", host="127.0.0.1", port=8080)

Or run:
    python -m dbini.server  # will start default project "dbini_project"
"""

from __future__ import annotations
import os
import json
import tempfile
import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, UploadFile, File, Body, WebSocket, WebSocketDisconnect, Depends, Query
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel, Field

from .core import DBini  # assumes core.py defines DBini
from .core import utcnow_iso

# ----------------- Pydantic Models -----------------
class DocumentCreate(BaseModel):
    doc: Dict[str, Any]
    doc_id: Optional[str] = None

class DocumentUpdate(BaseModel):
    updates: Dict[str, Any]

class UpsertRequest(BaseModel):
    filters: Dict[str, Any]
    updates: Dict[str, Any]
    doc_id: Optional[str] = None

class QueryRequest(BaseModel):
    filters: Optional[Dict[str, Any]] = None
    limit: Optional[int] = None
    sort: Optional[List[List]] = None  # [[field, direction], ...]
    search: Optional[str] = None

class BulkInsertRequest(BaseModel):
    docs: List[Dict[str, Any]]

class BulkUpdateRequest(BaseModel):
    filters: Dict[str, Any]
    updates: Dict[str, Any]

class BulkDeleteRequest(BaseModel):
    filters: Dict[str, Any]

class AggregateRequest(BaseModel):
    operation: str
    field: Optional[str] = None
    group_by: Optional[str] = None

class SchemaRequest(BaseModel):
    schema: Dict[str, Any]

# ----------------- Config / helpers -----------------
DEFAULT_PROJECT = "dbini_project"

def load_project_config(project_root: Path) -> Dict[str, Any]:
    cfg_path = project_root / "meta" / "project.json"
    if not cfg_path.exists():
        return {}
    try:
        return json.loads(cfg_path.read_text(encoding="utf-8"))
    except Exception:
        return {}

async def validate_api_key(project_root: Path, provided_key: Optional[str]) -> bool:
    """
    Optional lightweight API key check:
    If meta/project.json contains {"api_key": "..."} then provided_key must match.
    If no api_key set, allow access.
    """
    cfg = load_project_config(project_root)
    required = cfg.get("api_key")
    if not required:
        return True
    return provided_key == required

def require_key_dependency(project_root: Path):
    """
    Returns a FastAPI dependency function bound to project_root
    that checks X-Api-Key header.
    """
    async def _dep(x_api_key: Optional[str] = None):
        ok = await validate_api_key(project_root, x_api_key)
        if not ok:
            raise HTTPException(status_code=401, detail="Invalid API key")
    return _dep

def convert_sort_format(sort_list: Optional[List[List]]) -> Optional[List[tuple]]:
    """Convert [[field, direction], ...] to [(field, direction), ...]"""
    if not sort_list:
        return None
    return [(item[0], item[1]) for item in sort_list if len(item) == 2]

# ----------------- App factory -----------------
def create_app(project_root: str | Path = DEFAULT_PROJECT, *, allow_origins: Optional[List[str]] = None) -> FastAPI:
    project_root = Path(project_root)
    app = FastAPI(
        title="dbini - Enhanced NoSQL Database", 
        version="0.2.0",
        description="Complete NoSQL database with array operations, full-text search, and more"
    )

    # CORS
    origins = allow_origins or ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize DB instance and dependency
    db = DBini(project_root)
    require_key = require_key_dependency(project_root)

    # --------- Health & Info Endpoints ----------

    @app.get("/v1/health")
    async def health():
        valid, bad_line, msg = db.verify_wal()
        return {
            "status": "ok", 
            "wal_valid": valid, 
            "wal_bad_line": bad_line, 
            "wal_msg": msg,
            "version": "0.2.0"
        }

    @app.get("/v1/info")
    async def info():
        """Get database information"""
        collections = db.list_collections()
        files = db.list_files()
        
        total_docs = 0
        collection_stats = {}
        for collection in collections:
            stats = db.collection_stats(collection)
            collection_stats[collection] = stats
            total_docs += stats["document_count"]
        
        return {
            "collections": len(collections),
            "total_documents": total_docs,
            "total_files": len(files),
            "collection_stats": collection_stats
        }

    # --------- Collection Management ----------

    @app.get("/v1/collections")
    async def list_collections(dep=Depends(require_key)):
        """List all collections with stats"""
        collections = db.list_collections()
        result = []
        for collection in collections:
            stats = db.collection_stats(collection)
            result.append({
                "name": collection,
                "document_count": stats["document_count"],
                "size_mb": stats["total_size_mb"]
            })
        return {"collections": result}

    @app.get("/v1/collections/{collection}/stats")
    async def collection_stats(collection: str, dep=Depends(require_key)):
        """Get detailed statistics for a collection"""
        stats = db.collection_stats(collection)
        return {"collection": collection, "stats": stats}

    @app.post("/v1/collections/{collection}/index")
    async def create_index(collection: str, body: Dict[str, str] = Body(...), dep=Depends(require_key)):
        """Create an index on a field"""
        field = body.get("field")
        if not field:
            raise HTTPException(status_code=400, detail="Field name required")
        
        try:
            db.ensure_index_on(collection, field)
            return {"success": True, "collection": collection, "indexed_field": field}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # --------- Schema Management ----------

    @app.post("/v1/collections/{collection}/schema")
    async def set_schema(collection: str, request: SchemaRequest, dep=Depends(require_key)):
        """Set validation schema for a collection"""
        try:
            db.set_schema(collection, request.schema)
            return {"success": True, "collection": collection}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/v1/collections/{collection}/schema")
    async def get_schema(collection: str, dep=Depends(require_key)):
        """Get validation schema for a collection"""
        schema = db.get_schema(collection)
        if schema is None:
            raise HTTPException(status_code=404, detail="No schema found for collection")
        return {"collection": collection, "schema": schema}

    @app.delete("/v1/collections/{collection}/schema")
    async def delete_schema(collection: str, dep=Depends(require_key)):
        """Delete validation schema for a collection"""
        schema_file = db.meta / f"{collection}_schema.json"
        if schema_file.exists():
            schema_file.unlink()
            return {"success": True, "collection": collection}
        else:
            raise HTTPException(status_code=404, detail="No schema found for collection")

    # --------- Document CRUD ----------

    @app.post("/v1/collections/{collection}/documents")
    async def create_document(collection: str, request: DocumentCreate, dep=Depends(require_key)):
        """Create a new document with optional validation"""
        try:
            # Validate against schema if exists
            is_valid, errors = db.validate_document(collection, request.doc)
            if not is_valid:
                raise HTTPException(status_code=400, detail={"validation_errors": errors})
            
            doc_id = db.add_document(collection, request.doc, doc_id=request.doc_id)
            doc = db.get_document(collection, doc_id)
            return {"id": doc_id, "doc": doc, "created": True}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/v1/collections/{collection}/documents/{doc_id}")
    async def get_document(collection: str, doc_id: str, dep=Depends(require_key)):
        """Get a single document by ID"""
        doc = db.get_document(collection, doc_id)
        if doc is None:
            raise HTTPException(status_code=404, detail="Document not found")
        return {"id": doc_id, "doc": doc}

    @app.patch("/v1/collections/{collection}/documents/{doc_id}")
    async def update_document(collection: str, doc_id: str, request: DocumentUpdate, dep=Depends(require_key)):
        """Update a document (partial update)"""
        # Get current document to validate full document after update
        current_doc = db.get_document(collection, doc_id)
        if not current_doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Create merged document for validation
        merged_doc = {**current_doc, **request.updates}
        is_valid, errors = db.validate_document(collection, merged_doc)
        if not is_valid:
            raise HTTPException(status_code=400, detail={"validation_errors": errors})
        
        success = db.update_document(collection, doc_id, request.updates)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {"id": doc_id, "updated_at": utcnow_iso(), "success": True}

    @app.put("/v1/collections/{collection}/documents/upsert")
    async def upsert_document(collection: str, request: UpsertRequest, dep=Depends(require_key)):
        """Update document if exists, create if not (upsert)"""
        try:
            # Validate the merged document
            merged_doc = {**request.filters, **request.updates}
            is_valid, errors = db.validate_document(collection, merged_doc)
            if not is_valid:
                raise HTTPException(status_code=400, detail={"validation_errors": errors})
            
            doc_id, was_inserted = db.upsert_document(collection, request.filters, request.updates, request.doc_id)
            return {
                "id": doc_id, 
                "inserted": was_inserted, 
                "updated": not was_inserted,
                "timestamp": utcnow_iso()
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete("/v1/collections/{collection}/documents/{doc_id}")
    async def delete_document(collection: str, doc_id: str, dep=Depends(require_key)):
        """Delete a single document"""
        success = db.delete_document(collection, doc_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        return {"id": doc_id, "deleted": True, "timestamp": utcnow_iso()}

    # --------- Advanced Querying ----------

    @app.post("/v1/collections/{collection}:query")
    async def query_collection(collection: str, request: QueryRequest, dep=Depends(require_key)):
        """
        Advanced query with support for:
        - Complex filters ($and, $or, $not, $size, $elemMatch, $regex, etc.)
        - Full-text search
        - Sorting and limiting
        - Array operations
        """
        try:
            sort_tuples = convert_sort_format(request.sort)
            results = db.find(
                collection, 
                filters=request.filters, 
                limit=request.limit, 
                sort=sort_tuples,
                search=request.search
            )
            return {
                "count": len(results), 
                "results": results,
                "has_more": request.limit and len(results) == request.limit
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.get("/v1/collections/{collection}/documents")
    async def get_all_documents(
        collection: str, 
        limit: Optional[int] = Query(None, description="Limit number of results"),
        skip: Optional[int] = Query(0, description="Skip number of results"),
        search: Optional[str] = Query(None, description="Full-text search query"),
        dep=Depends(require_key)
    ):
        """Get all documents in collection with optional pagination and search"""
        try:
            # Simple pagination by getting more docs than needed and slicing
            fetch_limit = None
            if limit:
                fetch_limit = limit + (skip or 0)
            
            docs = db.find(collection, filters=None, limit=fetch_limit, search=search)
            
            # Apply skip manually
            if skip:
                docs = docs[skip:]
            
            # Apply final limit
            if limit:
                docs = docs[:limit]
            
            return {
                "count": len(docs), 
                "results": docs,
                "skip": skip or 0,
                "limit": limit
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/v1/collections/{collection}:aggregate")
    async def aggregate_collection(collection: str, request: AggregateRequest, dep=Depends(require_key)):
        """
        Perform aggregation operations:
        - count, min, max, avg, sum, distinct
        - Group by support
        """
        try:
            result = db.aggregate(collection, request.operation, request.field, request.group_by)
            return {
                "operation": request.operation,
                "field": request.field,
                "group_by": request.group_by,
                "result": result
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    # --------- Bulk Operations ----------

    @app.post("/v1/collections/{collection}/bulk:insert")
    async def bulk_insert(collection: str, request: BulkInsertRequest, dep=Depends(require_key)):
        """Insert multiple documents at once"""
        try:
            # Validate all documents if schema exists
            errors = []
            for i, doc in enumerate(request.docs):
                is_valid, doc_errors = db.validate_document(collection, doc)
                if not is_valid:
                    errors.append({"document_index": i, "errors": doc_errors})
            
            if errors:
                raise HTTPException(status_code=400, detail={"validation_errors": errors})
            
            doc_ids = db.bulk_insert(collection, request.docs)
            return {
                "inserted_count": len(doc_ids),
                "document_ids": doc_ids,
                "timestamp": utcnow_iso()
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/v1/collections/{collection}/bulk:update")
    async def bulk_update(collection: str, request: BulkUpdateRequest, dep=Depends(require_key)):
        """Update multiple documents matching filters"""
        try:
            updated_count = db.bulk_update(collection, request.filters, request.updates)
            return {
                "updated_count": updated_count,
                "timestamp": utcnow_iso()
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/v1/collections/{collection}/bulk:delete")
    async def bulk_delete(collection: str, request: BulkDeleteRequest, dep=Depends(require_key)):
        """Delete multiple documents matching filters"""
        try:
            deleted_count = db.bulk_delete(collection, request.filters)
            return {
                "deleted_count": deleted_count,
                "timestamp": utcnow_iso()
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # --------- File Management ----------

    @app.post("/v1/files")
    async def upload_file(file: UploadFile = File(...), dep=Depends(require_key)):
        """Upload a file"""
        # write to temp, then call db.save_file
        suffix = Path(file.filename or "unknown").suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp_path = Path(tmp.name)
            content = await file.read()
            tmp.write(content)
            tmp.flush()
            os.fsync(tmp.fileno())
        try:
            file_id = db.save_file(tmp_path, dest_filename=file.filename)
            return {
                "file_id": file_id,
                "filename": file.filename,
                "size": len(content),
                "uploaded_at": utcnow_iso()
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            try:
                tmp_path.unlink(missing_ok=True)
            except Exception:
                pass

    @app.get("/v1/files/{file_id}")
    async def download_file(file_id: str, dep=Depends(require_key)):
        """Download a file"""
        path = db.get_file_path(file_id)
        if not path:
            raise HTTPException(status_code=404, detail="File not found")
        return FileResponse(path, media_type="application/octet-stream", filename=Path(path).name)

    @app.get("/v1/files/{file_id}/info")
    async def file_info(file_id: str, dep=Depends(require_key)):
        """Get file metadata"""
        files = db.list_files()
        for f in files:
            if f["id"] == file_id:
                return f
        raise HTTPException(status_code=404, detail="File metadata not found")

    @app.get("/v1/files")
    async def list_files(dep=Depends(require_key)):
        """List all files with metadata"""
        files = db.list_files()
        return {"count": len(files), "files": files}

    @app.delete("/v1/files/{file_id}")
    async def delete_file(file_id: str, dep=Depends(require_key)):
        """Delete a file"""
        path = db.get_file_path(file_id)
        if not path:
            raise HTTPException(status_code=404, detail="File not found")
        
        try:
            # Remove file from filesystem
            Path(path).unlink()
            
            # Remove from files index
            fi = db.index_path / "files.index.sqlite"
            if fi.exists():
                import sqlite3
                conn = sqlite3.connect(str(fi))
                with conn:
                    conn.execute("DELETE FROM files WHERE id = ?", (file_id,))
                conn.close()
            
            return {"file_id": file_id, "deleted": True, "timestamp": utcnow_iso()}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # --------- Advanced Features ----------

    @app.post("/v1/collections/{collection}:validate")
    async def validate_document_endpoint(collection: str, doc: Dict[str, Any] = Body(...), dep=Depends(require_key)):
        """Validate a document against collection schema without storing it"""
        is_valid, errors = db.validate_document(collection, doc)
        return {
            "valid": is_valid,
            "errors": errors,
            "collection": collection
        }

    @app.post("/v1/export")
    async def export_database(body: Dict[str, str] = Body(...), dep=Depends(require_key)):
        """Export database snapshot"""
        export_path = body.get("export_path")
        if not export_path:
            raise HTTPException(status_code=400, detail="export_path required")
        
        try:
            snapshot_path = db.export_snapshot(export_path)
            return {
                "success": True,
                "snapshot_path": snapshot_path,
                "exported_at": utcnow_iso()
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/v1/restore")
    async def restore_database(body: Dict[str, str] = Body(...), dep=Depends(require_key)):
        """Restore database from snapshot"""
        snapshot_path = body.get("snapshot_path")
        if not snapshot_path:
            raise HTTPException(status_code=400, detail="snapshot_path required")
        
        try:
            db.restore_snapshot(snapshot_path)
            return {
                "success": True,
                "restored_from": snapshot_path,
                "restored_at": utcnow_iso()
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # --------- WebSocket Realtime ----------

    @app.websocket("/v1/ws/{collection}")
    async def websocket_collection_updates(websocket: WebSocket, collection: str, x_api_key: Optional[str] = None):
        """WebSocket for real-time collection updates"""
        # Validate API key for WebSocket
        allow = await validate_api_key(project_root, x_api_key)
        if not allow:
            await websocket.close(code=4401)
            return

        await websocket.accept()
        wal_file = db._wal_file
        
        try:
            # Send initial connection confirmation
            await websocket.send_json({
                "type": "connected",
                "collection": collection,
                "timestamp": utcnow_iso()
            })
            
            # Monitor WAL file for changes
            if not wal_file.exists():
                # Wait for WAL file to be created
                while not wal_file.exists():
                    await asyncio.sleep(0.5)
            
            with open(wal_file, "rb") as f:
                f.seek(0, os.SEEK_END)  # Start from end of file
                
                while True:
                    line = f.readline()
                    if not line:
                        # No new data, sleep and continue
                        await asyncio.sleep(0.2)
                        continue
                    
                    try:
                        obj = json.loads(line.decode("utf-8"))
                    except Exception:
                        # Skip corrupted lines
                        continue
                    
                    # Filter by collection if specified
                    if obj.get("collection") != collection:
                        continue
                    
                    # Send filtered WAL event
                    event = {
                        "type": "wal_event",
                        "operation": obj.get("op"),
                        "collection": obj.get("collection"),
                        "document_id": obj.get("id"),
                        "timestamp": obj.get("_ts"),
                        "fields": obj.get("fields")  # For update operations
                    }
                    
                    await websocket.send_json(event)
                    
        except WebSocketDisconnect:
            return
        except Exception as e:
            # Send error and close connection
            try:
                await websocket.send_json({
                    "type": "error",
                    "message": str(e),
                    "timestamp": utcnow_iso()
                })
            except Exception:
                pass
            return

    @app.websocket("/v1/ws")
    async def websocket_all_updates(websocket: WebSocket, x_api_key: Optional[str] = None):
        """WebSocket for all database updates"""
        allow = await validate_api_key(project_root, x_api_key)
        if not allow:
            await websocket.close(code=4401)
            return

        await websocket.accept()
        wal_file = db._wal_file
        
        try:
            await websocket.send_json({
                "type": "connected",
                "scope": "all_collections",
                "timestamp": utcnow_iso()
            })
            
            if not wal_file.exists():
                while not wal_file.exists():
                    await asyncio.sleep(0.5)
            
            with open(wal_file, "rb") as f:
                f.seek(0, os.SEEK_END)
                
                while True:
                    line = f.readline()
                    if not line:
                        await asyncio.sleep(0.2)
                        continue
                    
                    try:
                        obj = json.loads(line.decode("utf-8"))
                    except Exception:
                        continue
                    
                    # Send all WAL events
                    event = {
                        "type": "wal_event",
                        "operation": obj.get("op"),
                        "collection": obj.get("collection"),
                        "document_id": obj.get("id"),
                        "file_id": obj.get("file_id"),
                        "timestamp": obj.get("_ts"),
                        "fields": obj.get("fields")
                    }
                    
                    await websocket.send_json(event)
                    
        except WebSocketDisconnect:
            return
        except Exception:
            return

    # --------- Shutdown Handler ----------

    @app.on_event("shutdown")
    async def shutdown_event():
        """Clean shutdown"""
        try:
            db.close()
        except Exception:
            pass

    # Attach db instance for advanced usage
    app.state.db = db
    app.state.project_root = project_root

    return app

# ----------------- Run helper -----------------
def serve(project_root: str = DEFAULT_PROJECT, host: str = "127.0.0.1", port: int = 8080, allow_origins: Optional[List[str]] = None):
    """Start the enhanced DBini server"""
    app = create_app(project_root, allow_origins=allow_origins)
    print(f"🚀 Starting DBini Enhanced NoSQL Server")
    print(f"📁 Project: {project_root}")
    print(f"🌐 Server: http://{host}:{port}")
    print(f"📖 API Docs: http://{host}:{port}/docs")
    print(f"🔄 WebSocket: ws://{host}:{port}/v1/ws")
    uvicorn.run(app, host=host, port=port)

# ----------------- Module entrypoint -----------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run enhanced DBini server")
    parser.add_argument("--project", "-p", default=DEFAULT_PROJECT, help="project folder")
    parser.add_argument("--host", default="127.0.0.1", help="host")
    parser.add_argument("--port", "-P", default=8080, type=int, help="port")
    args = parser.parse_args()
    serve(args.project, host=args.host, port=args.port)