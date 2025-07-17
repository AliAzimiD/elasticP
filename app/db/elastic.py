# app/db/elastic.py
import time
from elasticsearch import Elasticsearch
from app.core.config import get_settings
from app.core.logger import logger

settings = get_settings()

def get_es_client(retries: int = 12, delay: int = 5) -> Elasticsearch:
    """Return an ES client, retrying <retries> times with <delay>s back‑off."""
    hosts = settings.es_host.split(",")
    for attempt in range(1, retries + 1):
        try:
            es = Elasticsearch(hosts)
            if es.ping():
                return es
        except Exception as exc:
            logger.warning("ES connection failed (attempt %d/%d): %s",
                           attempt, retries, exc)
        time.sleep(delay)
    raise ConnectionError(f"Cannot connect to Elasticsearch after {retries*delay}s")



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
