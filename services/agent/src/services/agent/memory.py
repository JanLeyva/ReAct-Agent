# 1st party
from urllib.parse import urlparse

# internal libs
from src.config import config
from src.shared.llm.factory import llm

# 3rd party libs
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.core.memory import (
    Memory,
    FactExtractionMemoryBlock,
    VectorMemoryBlock,
)

embed_model = GoogleGenAIEmbedding(
    model_name="text-embedding-004",
    embed_batch_size=100,
    api_key=config.api_key_google_genai,
)

uri = config.database_service_url
result = urlparse(uri)


def get_memory_session(chat_id: str) -> Memory:
    """
    Init a new memory object for the chat_id (user_id) is talking with the user.
    Args:
        chart_id (str): user is in Telegram
    Returns:
        Memory: object to handle memory using psotgres as vector database.
    """
    vector_store = PGVectorStore.from_params(
        database=result.path.lstrip("/"),
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

    return Memory.from_defaults(
        session_id=chat_id,
        async_database_uri=async_database_uri,
        memory_blocks=blocks,
        token_limit=4000,
        chat_history_token_ratio=0.7,
        token_flush_size=3000,
    )
