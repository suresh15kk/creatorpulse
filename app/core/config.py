from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://creator:secret@db:5432/creatorpulse"
    redis_url: str = "redis://redis:6379/0"

    # Security
    secret_key: str = "changeme"
    encryption_key: str = "changeme32charslong1234567890ab"

    # Google
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/auth/callback/google"

    # Meta (Instagram/Facebook)
    meta_client_id: str = ""
    meta_client_secret: str = ""
    meta_redirect_uri: str = "http://localhost:8000/auth/callback/instagram"

    # TikTok
    tiktok_client_key: str = ""
    tiktok_client_secret: str = ""
    tiktok_redirect_uri: str = "http://localhost:8000/auth/callback/tiktok"

    # OpenAI
    openai_api_key: str = ""

    # SendGrid
    sendgrid_api_key: str = ""
    from_email: str = "digest@creatorpulse.com"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()