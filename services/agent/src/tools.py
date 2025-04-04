# internal lib
from src.llm.factory import llm
# 3rd party
from llama_index.core.tools import FunctionTool
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.core.tools import QueryEngineTool
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# set LLM globaly
Settings.llm = llm
Settings.embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)
def add(x: int, y: int) -> int:
    """Useful function to add two numbers."""
    return x + y


def multiply(x: int, y: int) -> int:
    """Useful function to multiply two numbers."""
    return x * y


# load document
def create_retrival_engine():
    documents = SimpleDirectoryReader("/Users/esengineer/Documents/_dev/whatsapp-agent/docs/docs_barcelona/").load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    return QueryEngineTool.from_defaults(
        query_engine,
        name="turism_guide_Barcelona",
        description="A RAG engine with some basic facts about turism guide in Barcelona",
    )

budget_tool = create_retrival_engine()


tools = [
    budget_tool,
    FunctionTool.from_defaults(add),
    FunctionTool.from_defaults(multiply),
]
