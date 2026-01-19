"""
Configuration loader and settings manager.
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Centralized settings manager for the interview agent."""
    
    def __init__(self, config_path: str = None):
        """
        Initialize settings from config file.
        
        Args:
            config_path: Path to config.yaml file
        """
        if config_path is None:
            config_path = Path(__file__).parent / "config.yaml"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Replace environment variables
        config = self._replace_env_vars(config)
        return config
    
    def _replace_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Replace ${VAR} patterns with environment variables."""
        if isinstance(config, dict):
            return {k: self._replace_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._replace_env_vars(item) for item in config]
        elif isinstance(config, str) and config.startswith("${") and config.endswith("}"):
            var_name = config[2:-1]
            return os.getenv(var_name, "")
        return config
    
    def _validate_config(self):
        """Validate required configuration fields."""
        required_sections = ['llm', 'interview', 'logging']
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required config section: {section}")
    
    def get(self, key: str, default=None):
        """
        Get configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'llm.model')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    @property
    def llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration."""
        return self.config.get('llm', {})
    
    @property
    def interview_config(self) -> Dict[str, Any]:
        """Get interview configuration."""
        return self.config.get('interview', {})
    
    @property
    def groq_api_key(self) -> str:
        """Get Groq API key."""
        return self.get('api_keys.groq_api_key') or os.getenv('GROQ_API_KEY', '')
    
    @property
    def openai_api_key(self) -> str:
        """Get OpenAI API key."""
        return self.get('api_keys.openai_api_key') or os.getenv('OPENAI_API_KEY', '')


# Global settings instance
settings = Settings()
