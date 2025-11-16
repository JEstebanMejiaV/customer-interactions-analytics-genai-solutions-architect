from fastapi.testclient import TestClient
from fastapi import HTTPException

from app import db
from app.api import app, encode_cursor, decode_cursor


def _client_with_temp_db(tmp_path):
    """
    Configura una DB SQLite temporal, la inicializa con init_db
    y devuelve un TestClient para la FastAPI app.
    """
    test_db_path = tmp_path / "interactions_api_test.db"
    db.DB_PATH = str(test_db_path)
    db.init_db()
    return TestClient(app)


def test_encode_decode_cursor_roundtrip():
    last_id = 42
    cursor = encode_cursor(last_id)
    assert isinstance(cursor, str)

    decoded = decode_cursor(cursor)
    assert decoded == last_id


def test_decode_cursor_invalid_raises_http_exception():
    import pytest

    with pytest.raises(HTTPException):
        decode_cursor("not-a-valid-cursor")


def test_get_interactions_first_page_ok(tmp_path):
    client = _client_with_temp_db(tmp_path)

    account = "ACC-001"
    response = client.get(f"/interactions/{account}?limit=2")
    assert response.status_code == 200

    payload = response.json()
    assert payload["account_number"] == account
    assert "items" in payload
    assert isinstance(payload["items"], list)
    assert 1 <= len(payload["items"]) <= 2

    for item in payload["items"]:
        assert item["account_number"] == account
        assert "timestamp" in item


def test_get_interactions_returns_404_when_no_data(tmp_path):
    client = _client_with_temp_db(tmp_path)

    response = client.get("/interactions/UNKNOWN-ACCOUNT?limit=5")
    assert response.status_code == 404


def test_get_interactions_cursor_paginates(tmp_path):
    client = _client_with_temp_db(tmp_path)

    account = "ACC-001"

    # Primera página con límite pequeño para forzar paginación
    r1 = client.get(f"/interactions/{account}?limit=1")
    assert r1.status_code == 200
    p1 = r1.json()
    assert len(p1["items"]) == 1
    first_id = p1["items"][0]["id"]
    cursor = p1.get("next_cursor")

    # Si hay cursor, la siguiente página debe devolver otro registro
    if cursor:
        r2 = client.get(f"/interactions/{account}?limit=1&cursor={cursor}")
        assert r2.status_code == 200
        p2 = r2.json()
        assert len(p2["items"]) == 1
        second_id = p2["items"][0]["id"]
        assert second_id != first_id
