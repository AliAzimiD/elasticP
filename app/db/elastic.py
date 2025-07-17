"""
Elasticsearch client factory, plus index creation and health checks.
"""

from elasticsearch import Elasticsearch, NotFoundError, TransportError
from elasticsearch.helpers import bulk
from app.core.config import get_settings
from app.core.logger import logger

settings = get_settings()


def get_es_client() -> Elasticsearch:
    """
    Create a new Elasticsearch client instance.

    Called by FastAPI's dependency injection system
    so each request gets a lightweight reference (thread-safe).
    """
    es = Elasticsearch(settings.es_host.split(","))  # support multiple hosts
    if not es.ping():
        raise ConnectionError(f"Cannot connect to Elasticsearch at {settings.es_host}")
    return es


def create_index_if_missing(es: Elasticsearch) -> None:
    """
    Ensure our target index exists and has the right mapping.
    """
    index_name = settings.es_index

    if es.indices.exists(index=index_name):
        logger.info("Index '%s' already present – skipping creation.", index_name)
        return

    # Dynamic template: any field inside `body.*` becomes `text`
    mapping = {
        "mappings": {
            "properties": {
                "identifier": {"type": "keyword"},
                "body": {"type": "object", "dynamic": True},
            },
            "dynamic_templates": [
                {
                    "body_fields": {
                        "path_match": "body.*",
                        "mapping": {"type": "text"},
                    }
                }
            ],
        }
    }

    es.indices.create(index=index_name, body=mapping)
    logger.info("Created index '%s' with dynamic body mapping.", index_name)
