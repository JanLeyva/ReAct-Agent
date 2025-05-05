# internal lib
from src.react_agent import ReActAgent
from src.llm.factory import llm
from src.tools import tools
import asyncio

# 3rd party
from fastapi import FastAPI
from pydantic import BaseModel
from time import time
import uvicorn
from loguru import logger

agent = ReActAgent(llm=llm, tools=tools, timeout=120, verbose=True)
app = FastAPI()


class TelegramMsg(BaseModel):
    message: str
    chat_id: int


@app.get("/")
def health():
    return {"health": "OK"}


async def main(message: str) -> str:
    # Run the agent
    response = await agent.run(input=message)
    logger.info(response)
    return response["response"]


@app.post("/telegram/")
def get_agent_response(request: TelegramMsg):
    logger.info(f"message: {request.message}")
    message = asyncio.run(main(request.message))
    logger.info(f"response: {message} | chat_id: {request.chat_id}")

    return {
        "response": message,
        "chat_id": request.chat_id,
        "timestamp": time(),
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
