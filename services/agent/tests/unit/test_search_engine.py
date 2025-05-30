# internal libs
from api import app
from src.services.search_engine.vector_store import VectorStore

# 3rd party
import pytest
from fastapi.testclient import TestClient


client = TestClient(app)
vec = VectorStore()


@pytest.mark.parametrize(
    ("query"),
    ["Search a japanes restaurant", "recomend me an italian restaurant"],
)
def test_search_engine(query):
    result = vec.semantic_search(query)

    assert isinstance(result, str)
    assert len(result) > 0
    assert result[0] == "1"


@pytest.mark.parametrize(
    ("query", "lat", "long"),
    [
        ("Search a japanes restaurant", 100, 1),
        ("recomend me an italian restaurant", 100, 1),
    ],
)
def test_search_engine_query_coordinates(query, long, lat):
    result = vec.semantic_search_with_filter(query, long, lat)

    assert isinstance(result, str)
    assert len(result) > 0
    assert result[0] == "1"


# API
def test_search_engine_api():
    # Prepare the headers
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    # Prepare the JSON payload
    payload = {"query": "recomend an italian restaurant"}
    response = client.post("/search/query/", json=payload, headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body.get("response", {}), dict)


def test_search_engine_query_coordinates_api():
    # Prepare the headers
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    # Prepare the JSON payload
    payload = {"query": "recomend an italian restaurant", "long": 1, "lat": 100}
    response = client.post("/search/query_coordinates/", json=payload, headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body.get("response", {}), dict)
