# 1st party
import json
from typing import Optional
import requests

# 3rd party
from fastapi import APIRouter, Header, HTTPException
from loguru import logger
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.memory import BaseMemory
from llama_index.core.tools import FunctionTool
from starlette import status

# internal libs
from src.config import config
from src.services.agent.memory import get_memory_session
from src.shared.api.base import UpdateTelegram
from src.shared.llm.factory import llm

router = APIRouter(prefix="/generate", tags=["generate"])

def get_weather() -> str:
    """Usfeful for getting the weather for a given location."""
    return "test"

tool = FunctionTool.from_defaults(get_weather)
agent = FunctionAgent(llm=llm, tools=[tool])


async def _generate_response(message: str, memory: BaseMemory) -> str:
    # Run the agent
    response = await agent.run(message, memory=memory)
    logger.info(response)
    return response.response.blocks[0].text


@router.post("/telegram/")
async def get_agent_response(
    update: UpdateTelegram,
    x_telegram_bot_api_secret_token: Optional[str] = Header(None),
):
    """Endpoint to generate a response for a Telegram message."""
    if x_telegram_bot_api_secret_token != config.secret_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect secret_token"
        )

    message = update.message
    if not message or not message.text:
        return {"statusCode": 200, "body": json.dumps("OK, no message to process")}

    chat_id = message.chat.id
    text = message.text
    logger.info(f"Processing message for chat_id: {chat_id}")

    memory = get_memory_session(str(chat_id))
    response_text = await _generate_response(text, memory)

    requests.post(
        f"https://api.telegram.org/bot{config.api_key_bot_telegram}/sendMessage",
        json={"chat_id": chat_id, "text": response_text, "parse_mode": "HTML"},
    )

    return {"statusCode": 200, "body": json.dumps("OK")}