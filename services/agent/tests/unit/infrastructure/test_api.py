# internal libs
from api import app

# 3rd party
from fastapi.testclient import TestClient

client = TestClient(app)


def test_returns_200_ok():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "OK"}
