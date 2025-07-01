# 1st party
import json
from typing import Optional
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


# Define Pydantic models to match Telegram's Update structure
class User(BaseModel):
    id: int
    is_bot: bool
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None


class Chat(BaseModel):
    id: int
    type: str
    title: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class Message(BaseModel):
    message_id: int
    from_user: Optional[User] = None
    chat: Chat
    date: int
    text: Optional[str] = None


class CallbackQuery(BaseModel):
    id: str
    from_user: User
    message: Optional[Message] = None
    inline_message_id: Optional[str] = None
    chat_instance: str
    data: Optional[str] = None


class UpdateTelegram(BaseModel):
    update_id: int
    message: Optional[Message] = None
    edited_message: Optional[Message] = None
    callback_query: Optional[CallbackQuery] = None
    poll: Optional[dict] = None
    poll_answer: Optional[dict] = None
    secret_token: Optional[str] = None


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
def get_agent_response(update: UpdateTelegram):
    if update.secret_token == config.secret_token:
        message = update.message
        chat_id = message.chat.id
        text = message.text
        logger.info(f"response: {message} | chat_id: {chat_id}")
        if text:
            response = asyncio.run(generate(text))
            requests.post(
                f"https://api.telegram.org/bot{config.api_key_bot_telegram}/sendMessage",
                json={"chat_id": chat_id, "text": response},
            )
        return {"statusCode": 200, "body": json.dumps("OK")}
    return {"statusCode": 401, "body": json.dumps("Access denied")}


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
