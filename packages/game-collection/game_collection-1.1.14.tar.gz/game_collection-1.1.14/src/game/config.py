"""Configuration management for the game collection."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import appdirs


class Config:
    """Configuration manager for the game collection."""

    def __init__(self) -> None:
        """Initialize the configuration manager."""
        self._config_data: dict[str, Any] = {}
        self._config_path = self._get_config_path()
        self._load_config()

    def _get_config_path(self) -> Path:
        """Get the path to the configuration file."""
        # Use appdirs to get the appropriate config directory
        config_dir = Path(appdirs.user_config_dir("GameCollection", "hleserg"))
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "config.json"

    def _load_config(self) -> None:
        """Load configuration from file."""
        # First try to load from user config directory
        if self._config_path.exists():
            try:
                with open(self._config_path, encoding="utf-8") as f:
                    self._config_data = json.load(f)
                return
            except (json.JSONDecodeError, OSError):
                # If user config is corrupted, fall back to default
                pass

        # Fall back to default config from package
        try:
            default_config_path = Path(__file__).parent / "config.json"
            if default_config_path.exists():
                with open(default_config_path, encoding="utf-8") as f:
                    self._config_data = json.load(f)
                # Save the default config to user directory
                self.save_config()
        except (json.JSONDecodeError, OSError):
            # If even default config fails, create minimal config
            self._config_data = self._get_default_config()

    def _get_default_config(self) -> dict[str, Any]:
        """Get default configuration."""
        return {
            "display": {"width": 800, "height": 600, "fullscreen": False, "fps": 60},
            "controls": {
                "snake": {
                    "up": "UP",
                    "down": "DOWN",
                    "left": "LEFT",
                    "right": "RIGHT",
                    "pause": "SPACE",
                },
                "tetris": {
                    "left": "LEFT",
                    "right": "RIGHT",
                    "down": "DOWN",
                    "rotate": "UP",
                    "drop": "SPACE",
                    "pause": "ESCAPE",
                },
                "arkanoid": {
                    "left": "LEFT",
                    "right": "RIGHT",
                    "launch": "SPACE",
                    "pause": "ESCAPE",
                },
                "pacman": {
                    "up": "UP",
                    "down": "DOWN",
                    "left": "LEFT",
                    "right": "RIGHT",
                    "pause": "SPACE",
                },
            },
            "game_settings": {
                "snake": {"speed": 10, "grid_size": 20, "initial_length": 3},
                "tetris": {"speed": 1, "grid_width": 10, "grid_height": 20, "drop_speed": 0.5},
                "arkanoid": {
                    "paddle_speed": 8,
                    "ball_speed": 5,
                    "lives": 3,
                    "block_rows": 5,
                    "block_cols": 10,
                },
                "pacman": {
                    "speed": 3,
                    "ghost_speed": 2,
                    "dots_per_row": 19,
                    "dots_per_col": 21,
                    "lives": 3,
                },
            },
            "audio": {
                "enabled": True,
                "volume": 0.7,
                "music_volume": 0.5,
                "sound_effects_volume": 0.8,
            },
            "difficulty": {
                "easy": {
                    "snake_speed": 8,
                    "tetris_speed": 0.8,
                    "arkanoid_ball_speed": 4,
                    "pacman_ghost_speed": 1.5,
                },
                "normal": {
                    "snake_speed": 10,
                    "tetris_speed": 1.0,
                    "arkanoid_ball_speed": 5,
                    "pacman_ghost_speed": 2.0,
                },
                "hard": {
                    "snake_speed": 12,
                    "tetris_speed": 1.2,
                    "arkanoid_ball_speed": 6,
                    "pacman_ghost_speed": 2.5,
                },
            },
            "current_difficulty": "normal",
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation."""
        keys = key.split(".")
        value = self._config_data

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value using dot notation."""
        keys = key.split(".")
        config = self._config_data

        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Set the value
        config[keys[-1]] = value

    def save_config(self) -> None:
        """Save configuration to file."""
        try:
            with open(self._config_path, "w", encoding="utf-8") as f:
                json.dump(self._config_data, f, indent=2, ensure_ascii=False)
        except OSError as e:
            print(f"Warning: Could not save config: {e}")

    def get_display_config(self) -> dict[str, Any]:
        """Get display configuration."""
        result = self.get("display", {})
        return result if isinstance(result, dict) else {}

    def get_controls_config(self, game: str) -> dict[str, str]:
        """Get controls configuration for a specific game."""
        result = self.get(f"controls.{game}", {})
        return result if isinstance(result, dict) else {}

    def get_game_settings(self, game: str) -> dict[str, Any]:
        """Get game settings for a specific game."""
        result = self.get(f"game_settings.{game}", {})
        return result if isinstance(result, dict) else {}

    def get_audio_config(self) -> dict[str, Any]:
        """Get audio configuration."""
        result = self.get("audio", {})
        return result if isinstance(result, dict) else {}

    def get_difficulty_config(self, difficulty: str | None = None) -> dict[str, Any]:
        """Get difficulty configuration."""
        if difficulty is None:
            difficulty = self.get("current_difficulty", "normal")
        result = self.get(f"difficulty.{difficulty}", {})
        return result if isinstance(result, dict) else {}

    def set_difficulty(self, difficulty: str) -> None:
        """Set the current difficulty level."""
        self.set("current_difficulty", difficulty)
        self.save_config()

    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults."""
        self._config_data = self._get_default_config()
        self.save_config()


# Global configuration instance
config = Config()
