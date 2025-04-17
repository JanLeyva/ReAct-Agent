import os
import logging
import sys
import asyncio
from src.llm.factory import llm
from src.llm.base import BaseLLM

from llama_index.core.workflow import Event
from llama_index.core.workflow import (
    StartEvent,
    StopEvent,
    Workflow,
    step,
    Context
)
from llama_index.core.tools import FunctionTool
from llama_index.core.agent import FunctionCallingAgent


class QueryEvent(Event):
    query: str


class RAGWorkflow(Workflow):
    storage_dir = "./storage"
    llm: BaseLLM
    query_engine: VectorStoreIndex

    # the first step will be setup
    @step
    async def set_up(self, ctx: Context, ev: StartEvent) -> QueryEvent:

        if not ev.resume_file:
            raise ValueError("No resume file provided")

        # define an LLM to work with
        self.llm = llm

        # ingest the data and set up the query engine
        if os.path.exists(self.storage_dir):
            # you've already ingested your documents
            storage_context = StorageContext.from_defaults(persist_dir=self.storage_dir)
            index = load_index_from_storage(storage_context)
        else:
            # parse and load your documents
            documents = LlamaParse(
                result_type="markdown",
                content_guideline_instruction="This is a resume, gather related facts together and format it as bullet points with headers"
            ).load_data(ev.resume_file)
            # embed and index the documents
            index = VectorStoreIndex.from_documents(
                documents,
                embed_model=OpenAIEmbedding(model_name="text-embedding-3-small")
            )
            index.storage_context.persist(persist_dir=self.storage_dir)

        # either way, create a query engine
        self.query_engine = index.as_query_engine(llm=self.llm, similarity_top_k=5)

        # now fire off a query event to trigger the next step
        return QueryEvent(query=ev.query)

    # the second step will be to ask a question and return a result immediately
    @step
    async def ask_question(self, ctx: Context, ev: QueryEvent) -> StopEvent:
        response = self.query_engine.query(f"This is a question about the specific resume we have in our database: {ev.query}")
        return StopEvent(result=response.response)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
