"""Configuration management for Rezehor."""

from pathlib import Path
from typing import Any
from functools import lru_cache

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv


class AIConfig(BaseModel):
    """AI model configuration."""

    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4096
    temperature: float = 0.7


class ScreenCaptureConfig(BaseModel):
    """Screen capture settings."""

    format: str = "PNG"
    quality: int = 85


class MemoryConfig(BaseModel):
    """Memory and database settings."""

    database_path: Path = Path("data/memory.db")
    max_history: int = 100


class HotkeyConfig(BaseModel):
    """Keyboard shortcuts."""

    activate: str = "ctrl+shift+r"
    screenshot_analyze: str = "ctrl+shift+s"
    quick_ask: str = "ctrl+shift+q"


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str = "INFO"
    rotation: str = "500 MB"
    retention: str = "10 days"


class Settings(BaseSettings):
    """Application settings from environment."""

    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    log_level: str = Field(default="INFO", alias="REZEHOR_LOG_LEVEL")
    data_dir: Path = Field(default=Path("data"), alias="REZEHOR_DATA_DIR")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


class Config:
    """Main configuration class."""

    def __init__(
        self, config_path: Path = Path("config/settings.yaml")
    ) -> None:
        # Load environment variables
        load_dotenv()

        # Load YAML config
        with open(config_path) as f:
            config_data: dict[str, Any] = yaml.safe_load(f)

        # Parse configurations
        self.ai = AIConfig(**config_data["ai"])
        self.screen_capture = ScreenCaptureConfig(
            **config_data["screen_capture"]
        )
        self.memory = MemoryConfig(**config_data["memory"])
        self.hotkeys = HotkeyConfig(**config_data["hotkeys"])
        self.logging = LoggingConfig(**config_data["logging"])

        # Load environment settings
        self.settings = Settings()

        # Ensure data directories exist
        self._setup_directories()

    def _setup_directories(self) -> None:
        """Create necessary directories."""
        self.settings.data_dir.mkdir(exist_ok=True)
        (self.settings.data_dir / "logs").mkdir(exist_ok=True)
        self.memory.database_path.parent.mkdir(exist_ok=True)


@lru_cache(maxsize=1)
def get_config() -> Config:
    """Get cached configuration instance."""
    return Config()
