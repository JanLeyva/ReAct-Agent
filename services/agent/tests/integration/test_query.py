# internal libs
from api import app

# 3rd party
import pytest
from fastapi.testclient import TestClient

client = TestClient(app)


@pytest.mark.parametrize(
    ("query", "chat_id"),
    [
        ("Search a japanes restaurant", 123),
        ("recomend me an italian restaurant", 456),
    ],
)
def test_telegram_query_coordinates(query, chat_id):
    # Prepare the headers
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    # Prepare the JSON payload
    payload = {"message": query, "chat_id": chat_id}
    response = client.post("/generate/", json=payload, headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body.get("response", {}), str)
    assert isinstance(body.get("chat_id", {}), int)
    assert isinstance(body.get("timestamp", {}), float)
    assert "restaurant" in body.get("response", {})  # ?
