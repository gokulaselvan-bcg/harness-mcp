from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.db import SessionLocal, reset_database
from app.main import app


@pytest.fixture
def session():
    reset_database()
    s = SessionLocal()
    try:
        yield s
    finally:
        s.close()


@pytest.fixture
def client():
    reset_database()
    return TestClient(app)


def review_and_approve(client: TestClient) -> None:
    """Clear the HITL gate: review the management-prepared field, then approve."""
    st = client.get("/api/deal/state").json()
    fmap = {f["key"]: f for f in st["fields"]}
    client.patch(f"/api/deal/fields/{fmap['adjusted_ebitda']['id']}", json={"value": "1200"})
    r = client.post("/api/deal/fields/approve")
    assert r.status_code == 200, r.text


def drive_to_cam(client: TestClient) -> None:
    assert client.post("/api/deal/seed").status_code == 200
    assert client.post("/api/deal/extract").status_code == 200
    review_and_approve(client)
    assert client.post("/api/deal/score").status_code == 200
    assert client.post("/api/deal/diligence").status_code == 200
    assert client.post("/api/deal/cam/compile").status_code == 200
