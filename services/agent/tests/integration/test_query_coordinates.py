# internal libs
from api import app
from src.config import config

# 3rd party
import pytest
from fastapi.testclient import TestClient

client = TestClient(app)


@pytest.mark.parametrize(
    ("query", "chat_id"),
    [
        ("Search a japanes restaurant around sagrada familia.", 123),
        ("recomend me an italian restaurant near passeig de gracia", 456),
    ],
)
def test_telegram_query_coordinates(query, chat_id):
    # Prepare the headers
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    # Prepare the JSON payload
    payload = {
        "update_id": 800524573,
        "message": {
            "message_id": 800524573,
            "from": {"id": 800524573, "is_bot": False, "first_name": "Test"},
            "chat": {"id": chat_id, "type": "private"},
            "date": 1678886400,
            "text": query,
        },
        "secret_token": config.secret_token,
    }
    response = client.post("/telegram/", json=payload, headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, dict)
    assert body.get("body") == '"OK"'
