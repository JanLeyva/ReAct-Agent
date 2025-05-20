# internal libs
from api import app
# 3rd party
from fastapi.testclient import TestClient

client = TestClient(app)

def test_telegram_post():
    # Prepare the headers
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    # Prepare the JSON payload
    payload = {"message": "Hi there", "chat_id": 123}
    response = client.post("/generate/", json=payload, headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body.get("response", {}), str)
    assert isinstance(body.get("chat_id", {}), int)
    assert isinstance(body.get("timestamp", {}), float)
