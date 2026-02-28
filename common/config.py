"""Common configuration loaded from environment / .env file."""
from __future__ import annotations

import os
from functools import lru_cache

# ---------------------------------------------------------------------------
# Try pydantic-settings first (pydantic v2), fall back to a simple
# dataclass-based config that reads os.environ directly.
# ---------------------------------------------------------------------------
try:
    from pydantic_settings import BaseSettings

    class Settings(BaseSettings):
        # OpenAI
        openai_api_key: str = ""
        openai_model: str = "gpt-4o"

        # SERP
        serp_api_key: str = ""

        # Email
        email_host: str = ""
        email_port: int = 587
        email_user: str = ""
        email_password: str = ""
        email_from: str = ""

        # Restaurant
        restaurant_name: str = "My Restaurant"
        restaurant_city: str = "New York"
        restaurant_neighborhood: str = "East Village"
        restaurant_cuisine: str = "Italian"
        restaurant_address: str = ""
        restaurant_phone: str = ""
        restaurant_hours: str = ""

        # Storage
        database_url: str = "sqlite:///./restaurant_bots.db"
        output_dir: str = "./outputs"

        model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

except ImportError:
    # Fallback: plain dataclass reading os.environ
    import dataclasses

    @dataclasses.dataclass
    class Settings:  # type: ignore[no-redef]
        openai_api_key: str = dataclasses.field(
            default_factory=lambda: os.environ.get("OPENAI_API_KEY", "")
        )
        openai_model: str = dataclasses.field(
            default_factory=lambda: os.environ.get("OPENAI_MODEL", "gpt-4o")
        )
        serp_api_key: str = dataclasses.field(
            default_factory=lambda: os.environ.get("SERP_API_KEY", "")
        )
        email_host: str = dataclasses.field(
            default_factory=lambda: os.environ.get("EMAIL_HOST", "")
        )
        email_port: int = dataclasses.field(
            default_factory=lambda: int(os.environ.get("EMAIL_PORT", "587"))
        )
        email_user: str = dataclasses.field(
            default_factory=lambda: os.environ.get("EMAIL_USER", "")
        )
        email_password: str = dataclasses.field(
            default_factory=lambda: os.environ.get("EMAIL_PASSWORD", "")
        )
        email_from: str = dataclasses.field(
            default_factory=lambda: os.environ.get("EMAIL_FROM", "")
        )
        restaurant_name: str = dataclasses.field(
            default_factory=lambda: os.environ.get("RESTAURANT_NAME", "My Restaurant")
        )
        restaurant_city: str = dataclasses.field(
            default_factory=lambda: os.environ.get("RESTAURANT_CITY", "New York")
        )
        restaurant_neighborhood: str = dataclasses.field(
            default_factory=lambda: os.environ.get("RESTAURANT_NEIGHBORHOOD", "East Village")
        )
        restaurant_cuisine: str = dataclasses.field(
            default_factory=lambda: os.environ.get("RESTAURANT_CUISINE", "Italian")
        )
        restaurant_address: str = dataclasses.field(
            default_factory=lambda: os.environ.get("RESTAURANT_ADDRESS", "")
        )
        restaurant_phone: str = dataclasses.field(
            default_factory=lambda: os.environ.get("RESTAURANT_PHONE", "")
        )
        restaurant_hours: str = dataclasses.field(
            default_factory=lambda: os.environ.get("RESTAURANT_HOURS", "")
        )
        database_url: str = dataclasses.field(
            default_factory=lambda: os.environ.get(
                "DATABASE_URL", "sqlite:///./restaurant_bots.db"
            )
        )
        output_dir: str = dataclasses.field(
            default_factory=lambda: os.environ.get("OUTPUT_DIR", "./outputs")
        )

        def __post_init__(self) -> None:
            # Load .env file if present
            env_file = os.path.join(os.getcwd(), ".env")
            if os.path.exists(env_file):
                with open(env_file) as fh:
                    for line in fh:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, _, val = line.partition("=")
                            os.environ.setdefault(key.strip(), val.strip())


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached singleton Settings instance."""
    return Settings()
