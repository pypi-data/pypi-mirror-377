"""Asset management utilities for PyInstaller builds."""

from __future__ import annotations

import sys
from pathlib import Path


def get_asset_path(relative_path: str | Path) -> Path:
    """
    Get the absolute path to an asset file.

    This function handles both development and PyInstaller builds:
    - In development: returns path relative to project root
    - In PyInstaller: returns path relative to sys._MEIPASS

    Args:
        relative_path: Path to asset relative to assets directory

    Returns:
        Absolute path to the asset file

    Example:
        >>> icon_path = get_asset_path("icon.ico")
        >>> font_path = get_asset_path("fonts/freesansbold.ttf")
    """
    # Running in PyInstaller bundle or development
    base_path = (
        Path(sys._MEIPASS) if hasattr(sys, "_MEIPASS") else Path(__file__).parent.parent.parent
    )

    # Ensure relative_path is a Path object
    if isinstance(relative_path, str):
        relative_path = Path(relative_path)

    # Build full path
    asset_path = base_path / "assets" / relative_path

    return asset_path


def get_config_path(relative_path: str | Path) -> Path:
    """
    Get the absolute path to a config file.

    This function handles both development and PyInstaller builds:
    - In development: returns path relative to src/game
    - In PyInstaller: returns path relative to sys._MEIPASS

    Args:
        relative_path: Path to config file relative to game directory

    Returns:
        Absolute path to the config file

    Example:
        >>> config_path = get_config_path("config.json")
    """
    # Running in PyInstaller bundle or development
    base_path = Path(sys._MEIPASS) if hasattr(sys, "_MEIPASS") else Path(__file__).parent

    # Ensure relative_path is a Path object
    if isinstance(relative_path, str):
        relative_path = Path(relative_path)

    # Build full path
    if hasattr(sys, "_MEIPASS"):
        # In PyInstaller, config is in the root
        config_path = base_path / relative_path
    else:
        # In development, config is in src/game
        config_path = base_path / relative_path

    return config_path


def asset_exists(relative_path: str | Path) -> bool:
    """
    Check if an asset file exists.

    Args:
        relative_path: Path to asset relative to assets directory

    Returns:
        True if asset exists, False otherwise
    """
    return get_asset_path(relative_path).exists()


def list_assets(subdirectory: str = "") -> list[Path]:
    """
    List all assets in a subdirectory.

    Args:
        subdirectory: Subdirectory within assets to list

    Returns:
        List of asset paths
    """
    assets_dir = get_asset_path(subdirectory)

    if not assets_dir.exists() or not assets_dir.is_dir():
        return []

    return list(assets_dir.iterdir())


# Convenience functions for common assets
def get_icon_path() -> Path:
    """Get path to the application icon."""
    return get_asset_path("icon.ico")


def get_font_path(font_name: str = "freesansbold.ttf") -> Path:
    """Get path to a font file."""
    return get_asset_path(f"fonts/{font_name}")


def get_sound_path(sound_name: str) -> Path:
    """Get path to a sound file."""
    return get_asset_path(f"sounds/{sound_name}")


def get_image_path(image_name: str) -> Path:
    """Get path to an image file."""
    return get_asset_path(f"images/{image_name}")


# Example usage and testing
if __name__ == "__main__":
    print("🔍 Asset path testing")
    print("=" * 40)

    # Test icon path
    icon_path = get_icon_path()
    print(f"📱 Icon: {icon_path}")
    print(f"   Exists: {icon_path.exists()}")

    # Test font path
    font_path = get_font_path()
    print(f"🔤 Font: {font_path}")
    print(f"   Exists: {font_path.exists()}")

    # Test config path
    config_path = get_config_path("config.json")
    print(f"⚙️ Config: {config_path}")
    print(f"   Exists: {config_path.exists()}")

    # Test PyInstaller detection
    print(f"📦 PyInstaller mode: {hasattr(sys, '_MEIPASS')}")
    if hasattr(sys, "_MEIPASS"):
        print(f"   MEIPASS: {sys._MEIPASS}")
