# app/db/elastic.py
import time
from elasticsearch import Elasticsearch
from app.core.config import get_settings
from app.core.logger import logger

settings = get_settings()
_hosts = settings.es_host.split(",")
_es: Elasticsearch | None = None      # cache

def _connect() -> Elasticsearch | None:
    try:
        es = Elasticsearch(_hosts, request_timeout=5)
        if es.ping():
            return es
    except Exception as exc:
        logger.warning("Elasticsearch unavailable: %s", exc)
    return None

def get_es_client(retries: int = 0, delay: int = 5) -> Elasticsearch:
    """
    Return a live ES client. If not yet reachable:
    • during startup: keep retrying (blocking)        when retries > 0
    • during request: raise HTTP 503 so caller can decide
    """
    global _es
    if _es and _es.ping():
        return _es

    attempts = retries or 1
    for attempt in range(1, attempts + 1):
        es = _connect()
        if es:
            _es = es
            return _es
        if attempt < attempts:
            time.sleep(delay)

    raise ConnectionError("Elasticsearch still unreachable")


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
