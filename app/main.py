"""
Main FastAPI application instance.

Handles startup events (index creation) and includes routers.
"""

from fastapi import FastAPI
from app.core.config import get_settings
from app.core.logger import logger
from app.db.elastic import get_es_client, create_index_if_missing
from app.routers import documents

settings = get_settings()

app = FastAPI(
    title="Multilingual Document Service",
    version="1.0.0",
    description="REST API for indexing and searching multilingual documents using Elasticsearch.",
)

# Register routers
app.include_router(documents.router)


# Startup event to ensure Elasticsearch index is created
@app.on_event("startup")
def startup_event():
    # Wait up to ~60 s for ES
    es = get_es_client(retries=12, delay=5)
    create_index_if_missing(es)
    logger.info("Startup complete – service ready.")
