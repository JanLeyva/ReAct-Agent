from src.llm.factory import llm

from llama_index.core.agent.workflow import FunctionAgent


# Define a simple calculator tool
def multiply(a: float, b: float) -> float:
    """Useful for multiplying two numbers."""
    return a * b


# Create an agent workflow with our calculator tool
# Create an agent workflow with our calculator tool
agent = FunctionAgent(
    tools=[multiply],
    llm=llm,
    system_prompt="You are a helpful assistant that can multiply two numbers.",
)
