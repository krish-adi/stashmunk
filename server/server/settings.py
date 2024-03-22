from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8')

    openai_url: str
    openai_api_key: str
    unstructuredio_url: str
    unstructuredio_api_key: str


server_settings = ServerSettings()
