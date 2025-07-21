# 1st party
import json
from typing import Optional
import requests

# internal libs
from src.services.load_restaurants.upload_place import GetUploadPlace
from src.services.search_engine.vector_store import VectorStore
from src.shared.llm.factory import llm
from src.services.agent.memory import get_memory_session
from src.config import config
from src.shared.api.base import (
    UpdateTelegram,
    SearchEngineQuery,
    SearchEngineQueryCoord,
)

# 3rd party
import uvicorn
from fastapi import FastAPI, HTTPException, Header
from starlette import status

from loguru import logger
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.memory import BaseMemory
from llama_index.core.tools import FunctionTool


# agent = ReActAgent(llm=llm, tools=tools, timeout=120, verbose=True)
def get_weather() -> str:
    """Usfeful for getting the weather for a given location."""
    return "test"


tool = FunctionTool.from_defaults(
    get_weather,
)

agent = FunctionAgent(llm=llm, tools=[tool])
app = FastAPI()
vec = VectorStore()


@app.get("/")
def health():
    return {"message": "OK"}


async def generate(message: str, memory: BaseMemory) -> str:
    # Run the agent
    response = await agent.run(message, memory=memory)
    logger.info(response)
    return response.response.blocks[0].text


@app.post("/telegram/")
async def get_agent_response(
    update: UpdateTelegram,
    x_telegram_bot_api_secret_token: Optional[str] = Header(None),
):
    if x_telegram_bot_api_secret_token == config.secret_token:
        message = update.message
        chat_id = message.chat.id
        text = message.text
        logger.info(f"response: {message} | chat_id: {chat_id}")
        if text:
            memory = get_memory_session(str(chat_id))
            response = await generate(text, memory)
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
