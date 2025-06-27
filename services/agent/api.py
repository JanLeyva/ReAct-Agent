# internal lib
from src.services.load_restaurants.upload_place import GetUploadPlace
from src.services.agent.react_agent import ReActAgent
from src.services.search_engine.vector_store import VectorStore
from src.shared.llm.factory import llm
from src.services.agent.tools import tools

# 3rd party
import asyncio
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from time import time
from loguru import logger

agent = ReActAgent(llm=llm, tools=tools, timeout=120, verbose=True)
app = FastAPI()
vec = VectorStore()


class TelegramMsg(BaseModel):
    message: str
    chat_id: int


class SearchEngineQuery(BaseModel):
    query: str


class SearchEngineQueryCoord(SearchEngineQuery):
    long: float
    lat: float
    distance: int


@app.get("/")
def health():
    return {"message": "OK"}


async def main(message: str) -> str:
    # Run the agent
    response = await agent.run(input=message)
    logger.info(response)
    return response["response"]


@app.post("/generate/")
def get_agent_response(request: TelegramMsg):
    logger.info(f"message: {request.message}")
    message = asyncio.run(main(request.message))
    logger.info(f"response: {message} | chat_id: {request.chat_id}")

    return {
        "response": message,
        "chat_id": request.chat_id,
        "timestamp": time(),
    }


@app.post("/search/query/")
def get_restaurants_from_query(query: SearchEngineQuery):
    """Search restaurant from query"""
    results = vec.semantic_search(query.query)
    return {"message": "OK", "response": results}


@app.post("/search/query_coordinates/")
def get_restaurants_from_query_coordinates(query: SearchEngineQueryCoord):
    """Search restaurant from query and coordinates"""
    results = vec.semantic_search_with_filter(
        query.query, query.long, query.lat, query.distance
    )
    return {"message": "OK", "response": results}


@app.post("/upload/restaurant/{place_name}")
def upload_restaurant(place_name: str):
    """
    Upload restaurant to vector store
    """
    GetUploadPlace().get_upload_places_by_name(place_name)
    return {"message": f"Place '{place_name}' uploaded successfully."}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
