from typing import Literal, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    groq_api_key: str
    openai_api_key: Optional[str]
    api_key_bot_telegram: Optional[str]
    tavily_api_key: Optional[str]
    model_provider: Literal["groq", "openai"]
    model_name: Literal["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "gpt-4o-min"]


config = Config()
