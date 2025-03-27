# 1st party
from abc import ABC, abstractmethod
from enum import Enum

# internal lib
from ..config import config

# 3rd party
from llama_index.llms.groq import Groq
from llama_index.llms.openai import OpenAI


# Enum for more robust provider and model management
class ModelProvider(str, Enum):
    GROQ = "groq"
    OPENAI = "openai"


class ModelName(str, Enum):
    LLAMA3_70B = "llama-3.3-70b-versatile"
    LLAMA3_8B = "llama-3.1-8b-instant"
    CHATGPT4 = "gpt-4o-mini"


# Abstract base class for LLM
class BaseLLM(ABC):
    @abstractmethod
    def model(self):
        """Abstract method to generate text"""
        pass

    @abstractmethod
    def model_metadata(self) -> str:
        pass


# Concrete LLM implementations
class GroqLlama370b(BaseLLM):
    def __init__(self):
        super().__init__()
        self.llm = Groq(model=ModelName.LLAMA3_70B, api_key=config.groq_api_key)

    def model(self) -> Groq:
        return self.llm

    @property
    def model_metadata(self) -> str:
        return self.__class__.__name__


class GroqLlama38b(BaseLLM):
    def __init__(self):
        self.llm = Groq(model=ModelName.LLAMA3_8B, api_key=config.groq_api_key)

    def model(self) -> Groq:
        return self.llm

    @property
    def model_metadata(self) -> str:
        return self.__class__.__name__


class OpenAIChatGPT4(BaseLLM):
    def __init__(self):
        self.llm = OpenAI(model=ModelName.CHATGPT4, api_key=config.groq_api_key)

    def model(self) -> OpenAI:
        return self.llm

    @property
    def model_metadata(self) -> str:
        return self.__class__.__name__
