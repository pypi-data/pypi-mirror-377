# app/api/p2_embeddings.py
from __future__ import annotations
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel

from app.core.embeddings import (
    compute_embedding_from_text,
    index_vector,
    search_vector,
)

router = APIRouter(prefix="/embeddings", tags=["embeddings"])


class EmbeddingIndexRequest(BaseModel):
    id: str
    context_id: str
    object_id: Optional[str] = None
    vector: Optional[List[float]] = None
    text: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None


class EmbeddingSearchRequest(BaseModel):
    vector: Optional[List[float]] = None
    text: Optional[str] = None
    top_k: Optional[int] = 10


@router.post("/index")
def api_index_embedding(body: EmbeddingIndexRequest):
    """
    Index a single embedding record.
    Provide either `vector` or `text` (text will be embedded with the stub embedder).
    """
    if body.vector is None and body.text is None:
        raise HTTPException(status_code=400, detail="Provide either vector or text")

    vec = body.vector if body.vector is not None else compute_embedding_from_text(body.text)
    # store
    index_vector(id=body.id, context_id=body.context_id, object_id=body.object_id, vector=vec, meta=body.meta)
    return {"status": "ok", "id": body.id, "context_id": body.context_id}


@router.post("/search")
def api_search(body: EmbeddingSearchRequest):
    """
    Search embeddings. Provide `vector` or `text` (text will be embedded).
    """
    if body.vector is None and body.text is None:
        raise HTTPException(status_code=400, detail="Provide either vector or text as query")

    vec = body.vector if body.vector is not None else compute_embedding_from_text(body.text)  # type: ignore
    results = search_vector(query_vector=vec, top_k=body.top_k or 10)
    return {"results": results}
