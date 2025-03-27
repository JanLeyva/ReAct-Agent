# internal lib
from src.llm.factory import LLMFactory
from src.config import config

# 3rd party
from fastapi import FastAPI
from pydantic import BaseModel
from time import time
import uvicorn

app = FastAPI()


class TelegramMsg(BaseModel):
    message: str


@app.get("/")
def health():
    return {"health": "OK"}


@app.post("/telegram/")
def get_agent_response(request: TelegramMsg):
    factory = LLMFactory().get_llm(config.model_provider, config.model_name)
    llm = factory.model()

    return {
        "response": llm.complete(request.message).text,
        "model": factory.model_metadata,
        "timestamp": time(),
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
