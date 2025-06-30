# 1st party
import json
import requests

# internal libs
from src.services.load_restaurants.upload_place import GetUploadPlace
from src.services.agent.react_agent import ReActAgent
from src.services.search_engine.vector_store import VectorStore
from src.shared.llm.factory import llm
from src.services.agent.tools import tools
from src.config import config

# 3rd party
import asyncio
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from loguru import logger

agent = ReActAgent(llm=llm, tools=tools, timeout=120, verbose=True)
app = FastAPI()
vec = VectorStore()


class TelegramWebHook(BaseModel):
    body: str


class SearchEngineQuery(BaseModel):
    query: str


class SearchEngineQueryCoord(SearchEngineQuery):
    long: float
    lat: float
    distance: int


@app.get("/")
def health():
    return {"message": "OK"}


async def generate(message: str) -> str:
    # Run the agent
    response = await agent.run(input=message)
    logger.info(response)
    return response["response"]


@app.post("/telegram/")
def get_agent_response(request: TelegramWebHook):
    body = json.loads(request.get("body", "{}"))
    logger.info(f"message: {request.body}")
    message = body.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text")
    logger.info(f"response: {message} | chat_id: {request.chat_id}")
    if text:
        response = asyncio.run(generate(text))
        requests.post(
            f"https://api.telegram.org/bot{config.api_key_bot_telegram}/sendMessage",
            json={"chat_id": chat_id, "text": response},
        )
    return {"statusCode": 200, "body": json.dumps("OK")}


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
    uvicorn.run(app, host="0.0.0.0", port=80, log_level="debug")
