from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    api_key_google_genai: str
    database_service_url: str
    cohere_api_key: str
    table_name: str
    embedding_dimensions: int
    time_partition_interval: int


config = Config()
