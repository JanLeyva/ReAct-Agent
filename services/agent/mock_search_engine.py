from src.services.search_engine.vector_store import VectorStore

# 3rd party libs
from loguru import logger

if __name__ == "__main__":
    vec = VectorStore()
    result = vec.semantic_search_with_filter("japanes restaurant", lat=100, long=1)
    logger.info(result)
