from src.llm.factory import LLMFactory
from src.config import config


def get_agent_response(model, prompt: str):
    return model.complete(prompt)


if __name__ == "__main__":
    factory = LLMFactory()
    model = factory.get_llm(config.model_provider, config.model_name)
    model = model.model()
    prompt = input("Introduce your input here:")
    breakpoint()
    response = get_agent_response(model, prompt)
