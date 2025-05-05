import os
from typing import Literal, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    groq_api_key: str
    openai_api_key: Optional[str]
    api_key_bot_telegram: Optional[str]
    tavily_api_key: Optional[str]
    api_key_google_maps: Optional[str]
    api_key_opik: Optional[str]
    api_key_google_genai: Optional[str]
    opik_workspace: Optional[str]
    opik_project_name: Optional[str]
    model_provider: Literal["groq", "openai"]
    model_name: Literal["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "gpt-4o-min"]


config = Config()

# TODO: testing propuse, we can delete it in PROD
os.environ["OPIK_API_KEY"] = config.api_key_opik
os.environ["OPIK_WORKSPACE"] = config.opik_workspace
os.environ["OPIK_PROJECT_NAME"] = config.opik_project_name
os.environ["OPENAI_API_KEY"] = config.openai_api_key
