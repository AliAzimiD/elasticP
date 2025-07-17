# Multilingual Document Service

FastAPI REST service for indexing and searching multilingual documents on Elasticsearch.

## Features

* Dynamic **language-agnostic** `body` field (`{lang_code: text}`) using Elasticsearch *dynamic templates*.
* Two endpoints:
  * `POST /documents` – index or update a document.
  * `GET  /search`    – full-text search in a specific language.
* Auto-creates the index and mapping at startup if missing.
* Docker-Compose stack (Elasticsearch + API).
* Modular codebase, dependency-injected ES client, structured logging.

## Quick start (local dev)

```bash
git clone <repo-url>
cd multilingual-doc-service
cp .env .env.local      # adjust variables if desired
docker compose up --build
