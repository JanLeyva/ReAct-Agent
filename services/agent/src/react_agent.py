# 1st party libs
from typing import Any, List
import os

# internal libs
from src.templates.prompts import (
    CONTEXT_REACT_CHAT_SYSTEM_HEADER,
    ROUTER_PROMPT,
    ANSWER_PROMPT,
)
# 3rd party libs
from loguru import logger
from llama_index.core.workflow import StartEvent, StopEvent, Workflow, step, Context
from llama_index.core.workflow import Event
from llama_index.core.llms.llm import LLM
from llama_index.core.llms import ChatMessage
from llama_index.core.tools.types import BaseTool
from llama_index.core.tools import ToolSelection, ToolOutput
from llama_index.core.agent.react import ReActChatFormatter, ReActOutputParser
from llama_index.core.agent.react.types import (
    ActionReasoningStep,
    ObservationReasoningStep,
)
from llama_index.core.memory import (
    VectorMemory,
    SimpleComposableMemory,
    ChatMemoryBuffer,
)
from llama_index.core.base.llms.types import MessageRole
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.core import global_handler, set_global_handler


set_global_handler("opik",)
opik_callback_handler = global_handler
os.environ["TOKENIZERS_PARALLELISM"] = "false"
# Memory Long-Short Term
# TODO init qdrant database or similar
vector_memory = VectorMemory.from_defaults(
    vector_store=None,  # leave as None to use default in-memory vector store
    embed_model=FastEmbedEmbedding(model_name="BAAI/bge-small-en-v1.5"),
    retriever_kwargs={"similarity_top_k": 1},
)

chat_memory_buffer = ChatMemoryBuffer.from_defaults()


class InputEvent(Event):
    input: ChatMessage


class HistEvent(Event):
    input: List[ChatMessage]


class AgenticEvent(Event):
    pass


class AnswerAgent(Event):
    msg: ChatMessage


class MemEvent(Event):
    memory_msg: List[ChatMessage]


class StreamEvent(Event):
    delta: str


class ToolCallEvent(Event):
    tool_calls: list[ToolSelection]


class FunctionOutputEvent(Event):
    output: ToolOutput


class MemAgent(Workflow):
    def __init__(
        self,
        *args: Any,
        llm: LLM | None = None,
        tools: list[BaseTool] | None = None,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        self.tools = tools or []
        self.llm = llm
        self.prefix_messages = [
            ChatMessage(content=CONTEXT_REACT_CHAT_SYSTEM_HEADER, role="system")
        ]
        self.formatter = ReActChatFormatter.from_defaults("")
        self.output_parser = ReActOutputParser()
        self.memory = SimpleComposableMemory.from_defaults(
            primary_memory=chat_memory_buffer, secondary_memory_sources=[vector_memory]
        )

    @step
    async def entry_point_msg(self, ctx: Context, ev: StartEvent) -> InputEvent:
        """Init the user msg, in case need convert audio msg to text."""
        user_msg = ChatMessage(role="user", content=ev.input)
        # persistant memory across steps
        # init memory if needed
        memory = await ctx.get("memory", default=None)
        if not memory:
            memory = ChatMemoryBuffer.from_defaults(llm=self.llm)

        memory.put(user_msg)

        # clear current reasoning
        await ctx.set("current_reasoning", [])
        # set memory
        await ctx.set("memory", memory)

        return InputEvent(input=user_msg)

    @step
    async def router(self, ctx: Context, ev: InputEvent) -> AgenticEvent | AnswerAgent:
        """Step to decide if we need to use tools and React patern or not"""
        user_msg = ev.input

        input_llm = [ChatMessage(content=ROUTER_PROMPT, role=MessageRole.SYSTEM)] + [
            user_msg
        ]
        # request llm router
        response = self.llm.chat(input_llm)
        logger.info(response.message.content)

        if "react" in response.message.content:
            return AgenticEvent()
        return AnswerAgent(msg=user_msg)

    @step
    async def handle_memory(self, ctx: Context, ev: AnswerAgent) -> MemEvent:
        """Look for short/long term memories and prepare prompt to answer"""
        # get previous memories
        chat_history = self.get_all_messages(ev.msg.content)
        if self._verbose:
            logger.info(chat_history)
        # format the prompt with memory
        chat_history = chat_history + [
            ChatMessage(role=MessageRole.SYSTEM, content="Current user request below:"),
            ChatMessage(role=MessageRole.USER, content=ev.msg.content),
        ]
        # update memories
        self.memory.put(ChatMessage(role=MessageRole.USER, content=ev.msg.content))

        return MemEvent(memory_msg=chat_history)

    @step
    async def prepare_chat_history(self, ctx: Context, ev: AgenticEvent) -> HistEvent:
        # get chat history
        memory = await ctx.get("memory")
        chat_history = memory.get()
        current_reasoning = await ctx.get("current_reasoning", default=[])

        # format the prompt with react instructions
        llm_input = self.formatter.format(
            self.tools, chat_history, current_reasoning=current_reasoning
        )
        if self._verbose:
            logger.info(current_reasoning)
        return HistEvent(input=llm_input)

    @step
    async def handle_llm_input(
        self, ctx: Context, ev: HistEvent
    ) -> ToolCallEvent | StopEvent:
        chat_history = ev.input
        current_reasoning = await ctx.get("current_reasoning", default=[])

        response_gen = await self.llm.astream_chat(chat_history)
        async for response in response_gen:
            ctx.write_event_to_stream(StreamEvent(delta=response.delta or ""))

        try:
            reasoning_step = self.output_parser.parse(response.message.content)
            current_reasoning.append(reasoning_step)
            if self._verbose:
                logger.info(reasoning_step)

            if reasoning_step.is_done:
                await ctx.set("memory", chat_history)
                await ctx.set("current_reasoning", current_reasoning)

                sources = await ctx.get("sources", default=[])

                return StopEvent(
                    result={
                        "response": reasoning_step.response,
                        "sources": [sources],
                        "reasoning": current_reasoning,
                    }
                )
            elif isinstance(reasoning_step, ActionReasoningStep):
                tool_name = reasoning_step.action
                tool_args = reasoning_step.action_input
                return ToolCallEvent(
                    tool_calls=[
                        ToolSelection(
                            tool_id="fake",
                            tool_name=tool_name,
                            tool_kwargs=tool_args,
                        )
                    ]
                )
        except Exception as e:
            current_reasoning.append(
                ObservationReasoningStep(
                    observation=f"There was an error in parsing my reasoning: {e}"
                )
            )
            await ctx.set("current_reasoning", current_reasoning)

        # if no tool calls or final response, iterate again
        return StopEvent(result={"response": "Cannot answer"})

    @step
    async def handle_tool_calls(self, ctx: Context, ev: ToolCallEvent) -> AgenticEvent:
        tool_calls = ev.tool_calls
        tools_by_name = {tool.metadata.get_name(): tool for tool in self.tools}
        current_reasoning = await ctx.get("current_reasoning", default=[])
        sources = await ctx.get("sources", default=[])

        # call tools -- safely!
        for tool_call in tool_calls:
            tool = tools_by_name.get(tool_call.tool_name)
            if not tool:
                current_reasoning.append(
                    ObservationReasoningStep(
                        observation=f"Tool {tool_call.tool_name} does not exist"
                    )
                )
                continue

            try:
                tool_output = tool(**tool_call.tool_kwargs)
                sources.append(tool_output)
                current_reasoning.append(
                    ObservationReasoningStep(observation=tool_output.content)
                )
            except Exception as e:
                current_reasoning.append(
                    ObservationReasoningStep(
                        observation=f"Error calling tool {tool.metadata.get_name()}: {e}"
                    )
                )
        if self._verbose:
            logger.info(sources)
            logger.info(current_reasoning)
        # save new state in context
        await ctx.set("sources", sources)
        await ctx.set("current_reasoning", current_reasoning)

        # prep the next iteration
        return AgenticEvent()

    @step
    async def answer(self, ev: MemEvent) -> StopEvent:
        """Response user message"""
        input_llm = [
            ChatMessage(content=ANSWER_PROMPT, role=MessageRole.SYSTEM)
        ] + ev.memory_msg
        response = self.llm.chat(input_llm)

        logger.info(response)
        return StopEvent(result={"response": response.message.content})

    def get_all_messages(self, query: str) -> List[ChatMessage]:
        return self.memory.get(input=query)
