"""
Configuration management for AgentSpec.

Provides centralized configuration loading with priority hierarchy
and validation using JSON schemas.
"""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import jsonschema
import yaml
from jsonschema import ValidationError

from ..config import get_default_config_path


@dataclass
class ConfigSource:
    """Represents a configuration source with priority."""

    name: str
    path: Optional[Path]
    data: Dict[str, Any]
    priority: int  # Lower number = higher priority


class ConfigManager:
    """
    Manages configuration loading from multiple sources with priority hierarchy.

    Priority order (highest to lowest):
    1. Command-line arguments
    2. Environment variables
    3. Project-specific config file (.agentspec.yaml)
    4. User config file (~/.agentspec/config.yaml)
    5. System config file (/etc/agentspec/config.yaml)
    6. Default configuration
    """

    def __init__(self, project_path: Optional[Path] = None):
        self.project_path = project_path or Path.cwd()
        self._config: Dict[str, Any] = {}
        self._sources: List[ConfigSource] = []
        self._schema: Optional[Dict[str, Any]] = None

    def load_config(self, cli_args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Load configuration from all sources in priority order.

        Args:
            cli_args: Command-line arguments to override config

        Returns:
            Merged configuration dictionary
        """
        self._sources.clear()

        # Load from all sources
        self._load_default_config()
        self._load_system_config()
        self._load_user_config()
        self._load_project_config()
        self._load_environment_config()

        if cli_args:
            self._load_cli_config(cli_args)

        # Merge configurations by priority
        self._config = self._merge_configs()

        # Validate final configuration
        if self._schema:
            self.validate_config(self._config)

        return self._config

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        keys = key.split(".")
        value = self._config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation."""
        keys = key.split(".")
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def validate_config(self, config: Dict[str, Any]) -> None:
        """Validate configuration against schema."""
        if not self._schema:
            return

        try:
            jsonschema.validate(config, self._schema)
        except ValidationError as e:
            raise ConfigurationError(f"Configuration validation failed: {e.message}")

    def load_schema(self, schema_path: Path) -> None:
        """Load JSON schema for configuration validation."""
        try:
            with open(schema_path, "r") as f:
                self._schema = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ConfigurationError(f"Failed to load schema from {schema_path}: {e}")

    def _load_default_config(self) -> None:
        """Load default configuration."""
        default_path = get_default_config_path()
        config = self._load_yaml_file(default_path)
        if config:
            self._sources.append(
                ConfigSource(name="default", path=default_path, data=config, priority=6)
            )

    def _load_system_config(self) -> None:
        """Load system-wide configuration."""
        system_path = Path("/etc/agentspec/config.yaml")
        config = self._load_yaml_file(system_path)
        if config:
            self._sources.append(
                ConfigSource(name="system", path=system_path, data=config, priority=5)
            )

    def _load_user_config(self) -> None:
        """Load user-specific configuration."""
        user_path = Path.home() / ".agentspec" / "config.yaml"
        config = self._load_yaml_file(user_path)
        if config:
            self._sources.append(
                ConfigSource(name="user", path=user_path, data=config, priority=4)
            )

    def _load_project_config(self) -> None:
        """Load project-specific configuration."""
        project_path = self.project_path / ".agentspec.yaml"
        config = self._load_yaml_file(project_path)
        if config:
            self._sources.append(
                ConfigSource(name="project", path=project_path, data=config, priority=3)
            )

    def _load_environment_config(self) -> None:
        """Load configuration from environment variables."""
        env_config = {}
        prefix = "AGENTSPEC_"

        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix) :].lower().replace("_", ".")
                env_config[config_key] = self._parse_env_value(value)

        if env_config:
            self._sources.append(
                ConfigSource(name="environment", path=None, data=env_config, priority=2)
            )

    def _load_cli_config(self, cli_args: Dict[str, Any]) -> None:
        """Load configuration from command-line arguments."""
        if cli_args:
            self._sources.append(
                ConfigSource(name="cli", path=None, data=cli_args, priority=1)
            )

    def _load_yaml_file(self, path: Path) -> Optional[Dict[str, Any]]:
        """Load YAML file safely."""
        try:
            if path.exists():
                with open(path, "r") as f:
                    return yaml.safe_load(f) or {}
        except (yaml.YAMLError, IOError):
            # Silently ignore file loading errors
            pass
        return None

    def _parse_env_value(self, value: str) -> Union[str, int, float, bool]:
        """Parse environment variable value to appropriate type."""
        # Try boolean
        if value.lower() in ("true", "false"):
            return value.lower() == "true"

        # Try integer
        try:
            return int(value)
        except ValueError:
            pass

        # Try float
        try:
            return float(value)
        except ValueError:
            pass

        # Return as string
        return value

    def _merge_configs(self) -> Dict[str, Any]:
        """Merge configurations by priority (lower priority number wins)."""
        merged: Dict[str, Any] = {}

        # Sort by priority (highest priority first)
        sorted_sources = sorted(self._sources, key=lambda x: x.priority, reverse=True)

        for source in sorted_sources:
            merged = self._deep_merge(merged, source.data)

        return merged

    def _deep_merge(
        self, base: Dict[str, Any], override: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = base.copy()

        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def get_sources_info(self) -> List[Dict[str, Any]]:
        """Get information about loaded configuration sources."""
        return [
            {
                "name": source.name,
                "path": str(source.path) if source.path else None,
                "priority": source.priority,
                "keys": list(source.data.keys()),
            }
            for source in sorted(self._sources, key=lambda x: x.priority)
        ]


class ConfigurationError(Exception):
    """Configuration-related errors."""

    pass
