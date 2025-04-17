import json
from pathlib import Path
from typing import Any, Dict, Optional, cast

import aiohttp

from swipe_verse.models.config import GameConfig


class ConfigLoader:
    def __init__(self, base_path: Optional[str] = None):
        self.base_path = Path(base_path) if base_path else Path.cwd()

    async def load_config(self, config_path: str) -> GameConfig:
        """
        Load game configuration from file path or URL.

        Args:
            config_path: Path to config file or URL

        Returns:
            GameConfig: The loaded and validated game configuration
        """
        try:
            # Check if it's a URL
            if config_path.startswith(("http://", "https://")):
                config_data = await self._load_from_url(config_path)
            else:
                # Try as relative path, then absolute
                if not Path(config_path).is_absolute():
                    file_path = self.base_path / config_path
                else:
                    file_path = Path(config_path)

                config_data = self._load_from_file(file_path)

            # Parse using Pydantic for validation
            # Validate and return as GameConfig
            return cast(GameConfig, GameConfig.model_validate(config_data))

        except Exception as e:
            print(f"Error loading config: {e}")
            # Load kingdom config as fallback from bundled scenarios
            default_path = Path(__file__).parent.parent / "scenarios" / "kingdom_game.json"
            default_data = self._load_from_file(default_path)
            return cast(GameConfig, GameConfig.model_validate(default_data))

    def _load_from_file(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration from a local file"""
        if not file_path.exists():
            raise FileNotFoundError(f"Config file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            # json.load returns Any, cast to expected dict
            return cast(Dict[str, Any], json.load(f))

    async def _load_from_url(self, url: str) -> Dict[str, Any]:
        """Load configuration from a URL"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    # response.json() returns Any, cast to expected dict
                    return cast(Dict[str, Any], await response.json())
                else:
                    raise Exception(
                        f"Failed to download config from {url}, status {response.status}"
                    )

    async def merge_configs(
        self, base_config: GameConfig, override_config: Dict[str, Any]
    ) -> GameConfig:
        """
        Merge a base config with override values.

        Args:
            base_config: Base configuration to start with
            override_config: Dict with values to override in the base config

        Returns:
            GameConfig: Merged configuration
        """
        # Convert base config to dict
        base_dict = base_config.model_dump()

        # Deep merge the dictionaries
        merged = self._deep_merge(base_dict, override_config)

        # Validate and return new config
        # Validate merged config
        return cast(GameConfig, GameConfig.model_validate(merged))

    def _deep_merge(
        self, base: Dict[str, Any], override: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deep merge two dictionaries"""
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
