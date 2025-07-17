"""
Core CRUD operations abstracted away from routers.

Separating business logic keeps routers thin and testable.
"""

from typing import List
from elasticsearch import Elasticsearch
from app.core.config import get_settings
from app.core.logger import logger
from app.models.document import DocumentIn

settings = get_settings()
INDEX = settings.es_index


def upsert_document(es: Elasticsearch, doc: DocumentIn) -> None:
    """
    Create or update a document by ID.
    """
    logger.debug("Indexing document %s", doc.identifier)
    es.index(index=INDEX, id=doc.identifier, document=doc.model_dump())


def search_documents(
    es: Elasticsearch, lang: str, query: str, size: int = 10
) -> List[dict]:
    """
    Full-text search in a given language.

    Returns raw ES hits so caller can shape response.
    """
    field_name = f"body.{lang}"

    body = {
        "query": {
            "match": {
                field_name: {
                    "query": query,
                }
            }
        }
    }

    logger.debug("Executing search on '%s' for query='%s'", field_name, query)
    res = es.search(index=INDEX, body=body, size=size)
    return res["hits"]["hits"]
