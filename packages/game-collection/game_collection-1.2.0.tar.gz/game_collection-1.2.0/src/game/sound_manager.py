"""Sound management system for GameCollection."""

from __future__ import annotations

import pygame

from .assets import asset_exists, get_sound_path


class SoundManager:
    """Manages all game sounds and audio effects."""

    def __init__(self) -> None:
        """Initialize the sound manager."""
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self.enabled = True
        self.volume = 0.7
        self.music_volume = 0.5

        # Initialize pygame mixer if not already done
        try:
            mixer_init_status = pygame.mixer.get_init()
            if mixer_init_status is None:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        except pygame.error:
            # Fallback initialization if mixer fails
            pass

    def load_sound(self, sound_name: str, sound_path: str) -> bool:
        """
        Load a sound file.

        Args:
            sound_name: Name to store the sound under
            sound_path: Path to the sound file relative to assets/sounds

        Returns:
            True if sound loaded successfully, False otherwise
        """
        try:
            full_path = get_sound_path(sound_path)

            if not asset_exists(f"sounds/{sound_path}"):
                print(f"Warning: Sound file not found: {sound_path}")
                return False

            sound = pygame.mixer.Sound(str(full_path))
            self.sounds[sound_name] = sound
            return True

        except pygame.error as e:
            print(f"Warning: Could not load sound {sound_name}: {e}")
            # Create a silent sound as fallback
            try:
                # Create a very short silent sound
                silent_sound = pygame.mixer.Sound(b"\x00" * 1000)
                self.sounds[sound_name] = silent_sound
                return True
            except Exception:
                return False

    def play_sound(self, sound_name: str, volume: float | None = None) -> bool:
        """
        Play a sound effect.

        Args:
            sound_name: Name of the sound to play
            volume: Volume level (0.0 to 1.0), uses default if None

        Returns:
            True if sound played successfully, False otherwise
        """
        if not self.enabled:
            return False

        if sound_name not in self.sounds:
            print(f"Warning: Sound '{sound_name}' not loaded")
            return False

        try:
            sound = self.sounds[sound_name]
            if volume is not None:
                sound.set_volume(volume * self.volume)
            else:
                sound.set_volume(self.volume)

            sound.play()
            return True

        except pygame.error as e:
            print(f"Error playing sound {sound_name}: {e}")
            return False

    def stop_sound(self, sound_name: str) -> None:
        """Stop a specific sound."""
        if sound_name in self.sounds:
            self.sounds[sound_name].stop()

    def stop_all_sounds(self) -> None:
        """Stop all currently playing sounds."""
        pygame.mixer.stop()

    def set_volume(self, volume: float) -> None:
        """
        Set the master volume for sound effects.

        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.volume = max(0.0, min(1.0, volume))

    def set_music_volume(self, volume: float) -> None:
        """
        Set the volume for background music.

        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.music_volume = max(0.0, min(1.0, volume))

    def enable(self) -> None:
        """Enable sound effects."""
        self.enabled = True

    def disable(self) -> None:
        """Disable sound effects."""
        self.enabled = False
        self.stop_all_sounds()

    def is_enabled(self) -> bool:
        """Check if sound effects are enabled."""
        return self.enabled


class GameSoundManager(SoundManager):
    """Specialized sound manager for game-specific sounds."""

    def __init__(self) -> None:
        """Initialize the game sound manager."""
        super().__init__()
        self._load_game_sounds()

    def _load_game_sounds(self) -> None:
        """Load all game-specific sounds."""
        # Game start/end sounds
        self.load_sound("game_start", "game/start.wav")
        self.load_sound("game_over", "game/over.wav")
        self.load_sound("game_pause", "game/pause.wav")
        self.load_sound("game_resume", "game/resume.wav")

        # Score sounds
        self.load_sound("score", "effects/score.wav")
        self.load_sound("high_score", "effects/high_score.wav")
        self.load_sound("level_up", "effects/level_up.wav")

        # UI sounds
        self.load_sound("button_click", "ui/click.wav")
        self.load_sound("button_hover", "ui/hover.wav")
        self.load_sound("menu_open", "ui/menu_open.wav")
        self.load_sound("menu_close", "ui/menu_close.wav")

        # Snake game sounds
        self.load_sound("snake_eat", "game/snake_eat.wav")
        self.load_sound("snake_move", "game/snake_move.wav")
        self.load_sound("snake_crash", "game/snake_crash.wav")

        # Tetris game sounds
        self.load_sound("tetris_place", "game/tetris_place.wav")
        self.load_sound("tetris_line", "game/tetris_line.wav")
        self.load_sound("tetris_tetris", "game/tetris_tetris.wav")
        self.load_sound("tetris_rotate", "game/tetris_rotate.wav")

        # Arkanoid game sounds
        self.load_sound("arkanoid_hit", "game/arkanoid_hit.wav")
        self.load_sound("arkanoid_break", "game/arkanoid_break.wav")
        self.load_sound("arkanoid_paddle", "game/arkanoid_paddle.wav")
        self.load_sound("arkanoid_lose", "game/arkanoid_lose.wav")

        # Pac-Man game sounds
        self.load_sound("pacman_eat", "game/pacman_eat.wav")
        self.load_sound("pacman_power", "game/pacman_power.wav")
        self.load_sound("pacman_ghost", "game/pacman_ghost.wav")
        self.load_sound("pacman_die", "game/pacman_die.wav")

    def play_game_start(self) -> bool:
        """Play game start sound."""
        return self.play_sound("game_start")

    def play_game_over(self) -> bool:
        """Play game over sound."""
        return self.play_sound("game_over")

    def play_score(self) -> bool:
        """Play score sound."""
        return self.play_sound("score")

    def play_high_score(self) -> bool:
        """Play high score sound."""
        return self.play_sound("high_score")

    def play_level_up(self) -> bool:
        """Play level up sound."""
        return self.play_sound("level_up")

    def play_button_click(self) -> bool:
        """Play button click sound."""
        return self.play_sound("button_click")

    def play_button_hover(self) -> bool:
        """Play button hover sound."""
        return self.play_sound("button_hover")


# Global sound manager instance
sound_manager = GameSoundManager()


# Convenience functions for easy access
def play_sound(sound_name: str, volume: float | None = None) -> bool:
    """Play a sound effect."""
    return sound_manager.play_sound(sound_name, volume)


def play_game_start() -> bool:
    """Play game start sound."""
    return sound_manager.play_game_start()


def play_game_over() -> bool:
    """Play game over sound."""
    return sound_manager.play_game_over()


def play_score() -> bool:
    """Play score sound."""
    return sound_manager.play_score()


def play_button_click() -> bool:
    """Play button click sound."""
    return sound_manager.play_button_click()


def set_sound_volume(volume: float) -> None:
    """Set sound volume."""
    sound_manager.set_volume(volume)


def enable_sounds() -> None:
    """Enable sound effects."""
    sound_manager.enable()


def disable_sounds() -> None:
    """Disable sound effects."""
    sound_manager.disable()


def is_sound_enabled() -> bool:
    """Check if sounds are enabled."""
    return sound_manager.is_enabled()
