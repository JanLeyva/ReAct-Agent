# internal lib
from src.llm.factory import llm
# 3rd party
import qdrant_client
from llama_index.core.tools import FunctionTool
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.core.tools import QueryEngineTool
# from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.fastembed import FastEmbedEmbedding

# # set LLM globaly
# Settings.llm = llm
# Settings.embed_model = FastEmbedEmbedding(
#     model_name="BAAI/bge-small-en-v1.5"
# )
# def add(x: int, y: int) -> int:
#     """Useful function to add two numbers."""
#     return x + y


# def multiply(x: int, y: int) -> int:
#     """Useful function to multiply two numbers."""
#     return x * y



# client = qdrant_client.QdrantClient(
#     # you can use :memory: mode for fast and light-weight experiments,
#     # it does not require to have Qdrant deployed anywhere
#     # but requires qdrant-client >= 1.1.1
#     # location=":memory:"
#     # otherwise set Qdrant instance address with:
#     # url="http://:"
#     # otherwise set Qdrant instance with host and port:
#     host="localhost",
#     port=6333
#     # set API KEY for Qdrant Cloud
#     # api_key="",
# )

# # load document
# doc_path = "/Users/esengineer/Documents/_dev/whatsapp-agent/docs/docs_barcelona"
# documents = SimpleDirectoryReader(doc_path).load_data()
# vector_store = QdrantVectorStore(client=client, collection_name="turism_guide_Barcelona")
# storage_context = StorageContext.from_defaults(vector_store=vector_store)
# index = VectorStoreIndex.from_documents(
#     documents,
#     storage_context=storage_context,
# )

# query_engine = index.as_query_engine()
# vector_tool = QueryEngineTool.from_defaults(
#     query_engine=query_engine,
#     description=(
#         "Useful for retrieving specific context for turism in Barcelona"
#     ),
# )

# tools = [
#     vector_tool,
#     FunctionTool.from_defaults(add),
#     FunctionTool.from_defaults(multiply),
# ]
