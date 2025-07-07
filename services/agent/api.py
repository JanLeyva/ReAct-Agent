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
from fastapi import FastAPI, HTTPException, Header
from starlette import status
from pydantic import BaseModel
from loguru import logger

agent = ReActAgent(llm=llm, tools=tools, timeout=120, verbose=True)
app = FastAPI()
vec = VectorStore()


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
def get_agent_response(
    update: UpdateTelegram,
    x_telegram_bot_api_secret_token: Optional[str] = Header(None),
):
    if x_telegram_bot_api_secret_token == config.secret_token:
        message = update.message
        chat_id = message.chat.id
        text = message.text
        logger.info(f"response: {message} | chat_id: {chat_id}")
        if text:
            response = asyncio.run(generate(text))
            requests.post(
                f"https://api.telegram.org/bot{config.api_key_bot_telegram}/sendMessage",
                json={"chat_id": chat_id, "text": response, "parse_mode": "HTML"},
            )
        return {"statusCode": 200, "body": json.dumps("OK")}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect secret_token"
    )


@app.post("/search/query/")
def get_restaurants_from_query(
    query: SearchEngineQuery,
    x_telegram_bot_api_secret_token: Optional[str] = Header(None),
):
    """Search restaurant from query"""
    if x_telegram_bot_api_secret_token == config.secret_token:
        results = vec.semantic_search(query.query)
        return {"message": "OK", "response": results}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect secret_token"
    )


@app.post("/search/query_coordinates/")
def get_restaurants_from_query_coordinates(
    query: SearchEngineQueryCoord,
    x_telegram_bot_api_secret_token: Optional[str] = Header(None),
):
    """Search restaurant from query and coordinates"""
    if x_telegram_bot_api_secret_token == config.secret_token:
        results = vec.semantic_search_with_filter(
            query.query, query.long, query.lat, query.distance
        )
        return {"message": "OK", "response": results}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect secret_token"
    )


@app.post("/upload/restaurant/{place_name}")
def upload_restaurant(
    place_name: str, x_telegram_bot_api_secret_token: Optional[str] = Header(None)
):
    """
    Upload restaurant to vector store
    """
    if x_telegram_bot_api_secret_token == config.secret_token:
        GetUploadPlace().get_upload_places_by_name(place_name)
        return {"message": f"Place '{place_name}' uploaded successfully."}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect secret_token"
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80, log_level="debug")
