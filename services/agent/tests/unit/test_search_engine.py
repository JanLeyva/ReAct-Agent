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
    ("query", "lat", "long", "distance"),
    [
        ("Search a japanes restaurant", 31.25093516863868, 121.48219755115979, 1000),
        (
            "recomend me an italian restaurant",
            31.25093516863868,
            121.48219755115979,
            2000,
        ),
    ],
)
def test_search_engine_query_coordinates_no_results(query, long, lat, distance):
    result = vec.semantic_search_with_filter(query, long, lat, distance)

    assert len(result) > 0
    assert isinstance(result, str)
    assert result == "No Results where found for your localization"


@pytest.mark.parametrize(
    ("query", "lat", "long", "distance"),
    [
        ("Search a japanes restaurant", 41.40756379142826, 2.1724575744522867, 1000),
        (
            "recomend me an italian restaurant",
            41.3923748496093,
            2.165014450939276,
            2000,
        ),
    ],
)
def test_search_engine_query_coordinates(query, long, lat, distance):
    result = vec.semantic_search_with_filter(query, long, lat, distance)

    assert len(result) > 0
    assert isinstance(result, str)
    # assert result[0] == "1"


# API
@pytest.mark.parametrize(
    ("query"),
    ["Search a japanes restaurant", "recomend me an italian restaurant"],
)
def test_search_engine_api(query):
    # Prepare the headers
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    # Prepare the JSON payload
    payload = {"query": query}
    response = client.post("/search/query/", json=payload, headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body.get("response"), str)


@pytest.mark.parametrize(
    ("query", "lat", "long", "distance"),
    [
        ("Search a japanes restaurant", 31.25093516863868, 121.48219755115979, 1000),
        (
            "recomend me an italian restaurant",
            31.25093516863868,
            121.48219755115979,
            2000,
        ),
    ],
)
def test_search_engine_query_coordinates_no_results_api(query, lat, long, distance):
    # Prepare the headers
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    # Prepare the JSON payload
    payload = {"query": query, "long": long, "lat": lat, "distance": distance}
    response = client.post("/search/query_coordinates/", json=payload, headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body.get("response"), str)
    assert body.get("response") == "No Results where found for your localization"


# TODO uncomment test_search_engine_query_coordinates when we fill the db
@pytest.mark.parametrize(
    ("query", "lat", "long", "distance"),
    [
        ("Search a japanes restaurant", 41.40756379142826, 2.1724575744522867, 1000),
        (
            "recomend me an italian restaurant",
            41.3923748496093,
            2.165014450939276,
            2000,
        ),
    ],
)
def test_search_engine_query_coordinates_api(query, lat, long, distance):
    # Prepare the headers
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    # Prepare the JSON payload
    payload = {"query": query, "long": long, "lat": lat, "distance": distance}
    response = client.post("/search/query_coordinates/", json=payload, headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body.get("response"), str)
    assert len(body.get("response")) >= 20
