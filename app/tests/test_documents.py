"""
Basic integration test – requires ES running.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def _startup():
    # Trigger FastAPI startup event once
    with TestClient(app):
        pass


def test_create_and_search():
    payload = {
        "identifier": "42",
        "body": {"en": "hello world", "fa": "سلام دنیا"},
    }
    r = client.post("/documents", json=payload)
    assert r.status_code == 201

    r = client.get("/documents/search", params={"lang": "en", "query": "hello"})
    assert r.status_code == 200
    data = r.json()
    assert data and data[0]["identifier"] == "42"
