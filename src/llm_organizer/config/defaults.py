"""Default configuration and configuration loading utilities."""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from llm_organizer.config.schema import AppConfig, LLMConfig


def load_env_config() -> Dict[str, Any]:
    """Load configuration from environment variables."""
    load_dotenv()
    
    return {
        "llm": {
            "api_key": os.getenv("OPENAI_API_KEY", ""),
            "model_name": os.getenv("MODEL_NAME", "gpt-3.5-turbo"),
        }
    }


def load_yaml_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from a YAML file."""
    path = Path(config_path).expanduser()
    
    if not path.exists():
        return {}
        
    with open(path, 'r') as f:
        return yaml.safe_load(f) or {}


def load_json_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from a JSON file."""
    path = Path(config_path).expanduser()
    
    if not path.exists():
        return {}
        
    with open(path, 'r') as f:
        return json.load(f)


def load_config(config_path: Optional[str] = None) -> AppConfig:
    """
    Load configuration from multiple sources.
    
    Priority (highest to lowest):
    1. Provided config file
    2. User config file (~/.llm_organizer/config.yaml)
    3. Environment variables
    4. Default values from schema
    
    Args:
        config_path: Optional path to a config file
        
    Returns:
        AppConfig: Application configuration
    """
    config_data = {}
    
    # Load defaults from environment
    env_config = load_env_config()
    config_data.update(env_config)
    
    # Load user config if it exists
    user_config_path = Path("~/.llm_organizer/config.yaml").expanduser()
    if user_config_path.exists():
        user_config = load_yaml_config(str(user_config_path))
        config_data.update(user_config)
    
    # Load provided config if specified
    if config_path:
        path = Path(config_path).expanduser()
        if path.exists():
            if path.suffix.lower() in ('.yaml', '.yml'):
                file_config = load_yaml_config(str(path))
            elif path.suffix.lower() == '.json':
                file_config = load_json_config(str(path))
            else:
                raise ValueError(f"Unsupported config file format: {path.suffix}")
                
            config_data.update(file_config)
    
    # Create and validate config
    return AppConfig(**config_data)


def get_default_config() -> AppConfig:
    """Get the default configuration."""
    return AppConfig(
        llm=LLMConfig(
            api_key=os.getenv("OPENAI_API_KEY", ""),
            model_name=os.getenv("MODEL_NAME", "gpt-3.5-turbo"),
        )
    ) 