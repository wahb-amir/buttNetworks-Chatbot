from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    app_env: str = "dev"

    # Groq
    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"
    
    supabase_url: str
    supabase_service_role_key: str

    internal_api_token :str

    # Embeddings
    embedding_model: str = "BAAI/bge-small-en-v1.5"


settings = Settings()