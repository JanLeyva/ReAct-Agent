import os
import json
import requests

# internal libs
from src.services.agent.react_agent import ReActAgent
from src.services.search_engine.vector_store import VectorStore
from src.shared.llm.factory import llm
from src.services.agent.tools import tools

# 3rd party
import asyncio
from loguru import logger

agent = ReActAgent(llm=llm, tools=tools, timeout=120, verbose=True)
vec = VectorStore()


async def generate(message: str) -> str:
    # Run the agent
    response = await agent.run(input=message)
    logger.info(response)
    return response["response"]


def handler(event, context):
    """Use Telegram Bot Webhook to recive and send messages"""
    logger.info(f"event {event}")
    body = json.loads(event.get("body", "{}"))
    message = body.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")
    logger.info(f"Received message: {text} from chat_id: {chat_id}")
    if text:
        response = asyncio.run(generate(text))
        # reply to user
        token = os.environ["TELEGRAM_TOKEN"]
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": response},
        )
    return {"statusCode": 200, "body": json.dumps("OK")}
