from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from elasticsearch import Elasticsearch, TransportError
from app.db.elastic import get_es_client
from app.models.document import DocumentIn, DocumentOut
from app.services.document_service import upsert_document, search_documents

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post(
    "",  # /documents
    status_code=status.HTTP_201_CREATED,
    response_model=None,
    summary="Create or update a multilingual document",
)
def create_document(
    doc: DocumentIn, es: Elasticsearch = Depends(get_es_client)
):
    try:
        upsert_document(es, doc)
    except TransportError as exc:
        # Bubble up Elasticsearch errors with clean HTTP mapping
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"status": "success"}


@router.get(
    "/search",
    response_model=List[DocumentOut],
    summary="Search documents in a specific language",
)
def search(
    lang: str = Query(..., min_length=2, max_length=5, description="Language code (e.g. en, fa)"),
    query: str = Query(..., min_length=1, description="Full-text query string"),
    es: Elasticsearch = Depends(get_es_client),
):
    hits = search_documents(es, lang, query)
    # Extract `_source` field from ES hits
    return [hit["_source"] for hit in hits]
