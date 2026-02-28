"""
Central configuration via environment variables (12-factor).
Load with: from infra.config import settings
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    # LLM
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    openai_max_tokens: int = Field(default=2048, alias="OPENAI_MAX_TOKENS")

    # SERP
    serp_api_key: str = Field(default="", alias="SERP_API_KEY")
    serp_api_base_url: str = Field(default="https://serpapi.com", alias="SERP_API_BASE_URL")

    # Email
    smtp_host: str = Field(default="smtp.gmail.com", alias="SMTP_HOST")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_user: str = Field(default="", alias="SMTP_USER")
    smtp_password: str = Field(default="", alias="SMTP_PASSWORD")

    # Social
    facebook_page_id: str = Field(default="", alias="FACEBOOK_PAGE_ID")
    facebook_access_token: str = Field(default="", alias="FACEBOOK_ACCESS_TOKEN")

    # Database
    database_url: str = Field(default="sqlite:///./restaurant_bots.db", alias="DATABASE_URL")

    # Restaurant
    restaurant_name: str = Field(default="My Restaurant", alias="RESTAURANT_NAME")
    restaurant_city: str = Field(default="Austin", alias="RESTAURANT_CITY")
    restaurant_neighborhood: str = Field(default="East Austin", alias="RESTAURANT_NEIGHBORHOOD")
    restaurant_cuisine: str = Field(default="Italian", alias="RESTAURANT_CUISINE")
    restaurant_website: str = Field(default="https://myrestaurant.com", alias="RESTAURANT_WEBSITE")
    restaurant_phone: str = Field(default="", alias="RESTAURANT_PHONE")
    restaurant_hours: str = Field(default="Mon-Sun 11am-10pm", alias="RESTAURANT_HOURS")

    # Outputs
    output_dir: Path = Field(default=Path("./outputs"), alias="OUTPUT_DIR")
    reports_dir: Path = Field(default=Path("./outputs/reports"), alias="REPORTS_DIR")

    model_config = {"populate_by_name": True, "extra": "ignore"}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
