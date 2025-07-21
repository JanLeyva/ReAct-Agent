# 1st party
from typing import Optional

# 3rd party
from fastapi import APIRouter, Header, HTTPException
from starlette import status

# internal libs
from src.config import config
from src.services.search_engine.vector_store import VectorStore
from src.shared.api.base import SearchEngineQuery, SearchEngineQueryCoord

router = APIRouter(prefix="/search", tags=["search"])
vec = VectorStore()


@router.post("/query/")
def get_restaurants_from_query(
    query: SearchEngineQuery,
    x_telegram_bot_api_secret_token: Optional[str] = Header(None),
):
    """Search restaurant from query"""
    if x_telegram_bot_api_secret_token != config.secret_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect secret_token"
        )
    results = vec.semantic_search(query.query)
    return {"message": "OK", "response": results}


@router.post("/query_coordinates/")
def get_restaurants_from_query_coordinates(
    query: SearchEngineQueryCoord,
    x_telegram_bot_api_secret_token: Optional[str] = Header(None),
):
    """Search restaurant from query and coordinates"""
    if x_telegram_bot_api_secret_token != config.secret_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect secret_token"
        )
    results = vec.semantic_search_with_filter(
        query.query, query.long, query.lat, query.distance
    )
    return {"message": "OK", "response": results}