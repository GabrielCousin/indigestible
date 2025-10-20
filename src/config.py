"""
Configuration management for the newsletter aggregator.
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class Config:
    """Manages application configuration."""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize configuration from YAML file.

        Args:
            config_path: Path to the configuration file
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            logger.error(f"Configuration file not found: {self.config_path}")
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)

        logger.info(f"Loaded configuration from {self.config_path}")
        return config

    @property
    def sources(self) -> list:
        """Get list of newsletter sources."""
        return self.config.get('sources', [])

    @property
    def ai_config(self) -> Dict[str, Any]:
        """Get AI configuration."""
        return self.config.get('ai', {})

    @property
    def github_config(self) -> Dict[str, Any]:
        """Get GitHub configuration."""
        return self.config.get('github', {})

    def get_enabled_sources(self) -> list:
        """Get only enabled sources."""
        return [s for s in self.sources if s.get('enabled', True)]
