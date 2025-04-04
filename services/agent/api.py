# internal lib
# from src.basic_agent import agent
from src.react_agent import ReActAgent
from src.llm.factory import llm

import asyncio

# 3rd party
from fastapi import FastAPI
from pydantic import BaseModel
from time import time
import uvicorn

# react agent

from llama_index.core.tools import FunctionTool


def add(x: int, y: int) -> int:
    """Useful function to add two numbers."""
    return x + y


def multiply(x: int, y: int) -> int:
    """Useful function to multiply two numbers."""
    return x * y


tools = [
    FunctionTool.from_defaults(add),
    FunctionTool.from_defaults(multiply),
]

agent = ReActAgent(llm=llm, tools=tools, timeout=120, verbose=True)


# create context
# ctx = Context(agent)
app = FastAPI()


class TelegramMsg(BaseModel):
    message: str


@app.get("/")
def health():
    return {"health": "OK"}


async def main(message: str) -> str:
    # Run the agent
    response = await agent.run(message)
    print(response)
    return response["response"]


@app.post("/telegram/")
def get_agent_response(request: TelegramMsg):
    message = asyncio.run(main(request.message))

    return {
        "response": message,
        "timestamp": time(),
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
