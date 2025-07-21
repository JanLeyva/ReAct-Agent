# 1st party
import json
from typing import Optional
import requests
from urllib.parse import urlparse

# internal libs
from src.services.load_restaurants.upload_place import GetUploadPlace
from src.services.agent.react_agent import ReActAgent
from src.services.search_engine.vector_store import VectorStore
from src.shared.llm.factory import llm
from src.services.agent.tools import tools
from src.config import config

# 3rd party
import uvicorn
from fastapi import FastAPI, HTTPException, Header
from starlette import status
from pydantic import BaseModel
from loguru import logger
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.memory import BaseMemory, Memory, FactExtractionMemoryBlock, VectorMemoryBlock
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.vector_stores.postgres import PGVectorStore
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
embed_model = GoogleGenAIEmbedding(
            model_name="text-embedding-004",
            embed_batch_size=100,
            api_key=config.api_key_google_genai,
        )

uri = config.database_service_url
result = urlparse(uri)


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


def get_memory_session(chat_id: str) -> Memory:
    """
    """
    vector_store = PGVectorStore.from_params(
        database=result.path.lstrip('/'),
        host=result.hostname,
        password=result.password,
        port=result.port,
        user=result.username,
        table_name="long-term-memory",
        embed_dim=config.embedding_dimensions,
        use_halfvec=True,  # Enable half precision
    )
    blocks = [
        FactExtractionMemoryBlock(
            name="extracted_info",
            llm=llm,
            max_facts=50,
            priority=1,
        ),
        VectorMemoryBlock(
            name="vector_memory",
            vector_store=vector_store,
            priority=2,
            embed_model=embed_model,
        ),
    ]
    
    async_database_uri = f"postgresql+asyncpg://{result.username}:{result.password}@{result.hostname}:{result.port}{result.path}"

    return Memory.from_defaults(session_id=chat_id,
                                async_database_uri=async_database_uri,
                                memory_blocks=blocks,
                                token_limit=4000,
                                chat_history_token_ratio=0.7,
                                token_flush_size=3000,
                                 )


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
            # chat_history = memory.get(messages=[...])
            # logger.info(f"chat_history: \n{chat_history}")

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
