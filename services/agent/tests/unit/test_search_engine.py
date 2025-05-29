# internal libs
from api import app

# 3rd party
from fastapi.testclient import TestClient

client = TestClient(app)


def test_search_engine_api():
    # Prepare the headers
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    # Prepare the JSON payload
    payload = {"query": "recomend an italian restaurant"}
    response = client.post("/search/query/", json=payload, headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body.get("response", {}), dict)


def test_search_engine_coordinates_api():
    # Prepare the headers
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    # Prepare the JSON payload
    payload = {"query": "recomend an italian restaurant", "long": 1, "lat": 100}
    response = client.post("/search/query_coordinates/", json=payload, headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body.get("response", {}), dict)
