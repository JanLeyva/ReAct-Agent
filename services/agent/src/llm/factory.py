# 1st party
from typing import Dict

# internal lib
from src.config import config

# 3rd party lib
from src.llm.base import (
    BaseLLM,
    ModelName,
    ModelProvider,
    GroqLlama370b,
    GroqLlama38b,
    OpenAIChatGPT4,
)


class LLMFactory:
    _providers: Dict[tuple[ModelProvider, ModelName], type[BaseLLM]] = {
        (ModelProvider.GROQ, ModelName.LLAMA3_70B): GroqLlama370b(),
        (ModelProvider.GROQ, ModelName.LLAMA3_8B): GroqLlama38b(),
        (ModelProvider.OPENAI, ModelName.CHATGPT4): OpenAIChatGPT4(),
    }

    @classmethod
    def get_llm(cls, model_provider: ModelProvider, model_name: ModelName) -> BaseLLM:
        """
        Factory method to create and return the appropriate LLM instance

        Args:
            model_provider (ModelProvider): The provider of the LLM
            model_name (ModelName): The specific model to use

        Returns:
            BaseLLM: An instance of the specified LLM

        Raises:
            ValueError: If the combination of provider and model is not supported
        """
        try:
            model = cls._providers[(model_provider, model_name)]
            return model
        except KeyError:
            raise ValueError(
                f"Unsupported combination: {model_provider} - {model_name}"
            )


factory = LLMFactory().get_llm(config.model_provider, config.model_name)
llm = factory.model()
