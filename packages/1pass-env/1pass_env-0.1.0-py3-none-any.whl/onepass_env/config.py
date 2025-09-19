"""Configuration management for 1pass-env."""

import os
from pathlib import Path
from typing import Dict, Optional

from pydantic import BaseModel, Field

from onepass_env.exceptions import ConfigurationError


class Config(BaseModel):
    """Configuration model for 1pass-env."""
    
    default_vault: Optional[str] = Field(default=None, description="Default 1Password vault")
    default_env_file: str = Field(default=".env", description="Default environment file")
    auto_sync: bool = Field(default=False, description="Automatically sync with 1Password")
    verbose: bool = Field(default=False, description="Enable verbose logging")
    
    class Config:
        """Pydantic configuration."""
        env_prefix = "ONEPASS_ENV_"


def load_config() -> Config:
    """Load configuration from environment variables and config file."""
    config_file = Path.home() / ".config" / "1pass-env" / "config.json"
    
    if config_file.exists():
        try:
            import json
            with open(config_file) as f:
                file_config = json.load(f)
            return Config(**file_config)
        except Exception as e:
            raise ConfigurationError(f"Failed to load config file: {e}")
    
    # Load from environment variables
    return Config()


def save_config(config: Config) -> None:
    """Save configuration to file."""
    config_dir = Path.home() / ".config" / "1pass-env"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    config_file = config_dir / "config.json"
    
    try:
        import json
        with open(config_file, "w") as f:
            json.dump(config.dict(), f, indent=2)
    except Exception as e:
        raise ConfigurationError(f"Failed to save config file: {e}")
