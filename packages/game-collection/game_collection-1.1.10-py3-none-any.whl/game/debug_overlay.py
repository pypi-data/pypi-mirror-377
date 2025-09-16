"""Debug overlay for FPS and status information."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from .config import Config


class DebugOverlay:
    """Debug overlay showing FPS and game status."""

    def __init__(self, screen: pygame.Surface, config: Config) -> None:
        """Initialize the debug overlay."""
        self.screen = screen
        self.config = config
        self.enabled = False
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)

        # FPS tracking
        self.fps_history: list[float] = []
        self.last_time = time.time()
        self.frame_count = 0

        # Status information
        self.current_game = "Menu"
        self.game_state = "running"
        self.mouse_pos = (0, 0)
        self.keys_pressed: list[str] = []

    def toggle(self) -> None:
        """Toggle the debug overlay on/off."""
        self.enabled = not self.enabled

    def update_fps(self, dt: float) -> None:  # noqa: ARG002
        """Update FPS calculation."""
        if not self.enabled:
            return

        current_time = time.time()
        self.frame_count += 1

        # Calculate FPS every second
        if current_time - self.last_time >= 1.0:
            fps = self.frame_count / (current_time - self.last_time)
            self.fps_history.append(fps)

            # Keep only last 10 FPS readings
            if len(self.fps_history) > 10:
                self.fps_history.pop(0)

            self.frame_count = 0
            self.last_time = current_time

    def update_status(self, current_game: str, game_state: str) -> None:
        """Update game status information."""
        self.current_game = current_game
        self.game_state = game_state

    def update_input(self, mouse_pos: tuple[int, int], keys_pressed: list[str]) -> None:
        """Update input information."""
        self.mouse_pos = mouse_pos
        self.keys_pressed = keys_pressed

    def draw(self) -> None:
        """Draw the debug overlay."""
        if not self.enabled:
            return

        # Background
        overlay_surface = pygame.Surface((300, 200))
        overlay_surface.set_alpha(200)
        overlay_surface.fill((0, 0, 0))

        y_offset = 10

        # Title
        title_text = self.font.render("DEBUG OVERLAY", True, (255, 255, 0))
        overlay_surface.blit(title_text, (10, y_offset))
        y_offset += 30

        # FPS information
        if self.fps_history:
            avg_fps = sum(self.fps_history) / len(self.fps_history)
            fps_text = self.small_font.render(f"FPS: {avg_fps:.1f}", True, (0, 255, 0))
            overlay_surface.blit(fps_text, (10, y_offset))
            y_offset += 20

            min_fps = min(self.fps_history)
            max_fps = max(self.fps_history)
            fps_range_text = self.small_font.render(
                f"Range: {min_fps:.1f} - {max_fps:.1f}", True, (0, 255, 0)
            )
            overlay_surface.blit(fps_range_text, (10, y_offset))
            y_offset += 20

        # Game status
        game_text = self.small_font.render(f"Game: {self.current_game}", True, (255, 255, 255))
        overlay_surface.blit(game_text, (10, y_offset))
        y_offset += 20

        state_text = self.small_font.render(f"State: {self.game_state}", True, (255, 255, 255))
        overlay_surface.blit(state_text, (10, y_offset))
        y_offset += 20

        # Mouse position
        mouse_text = self.small_font.render(f"Mouse: {self.mouse_pos}", True, (255, 255, 255))
        overlay_surface.blit(mouse_text, (10, y_offset))
        y_offset += 20

        # Keys pressed
        if self.keys_pressed:
            keys_text = self.small_font.render(
                f"Keys: {', '.join(self.keys_pressed)}", True, (255, 255, 255)
            )
            overlay_surface.blit(keys_text, (10, y_offset))
            y_offset += 20

        # Instructions
        instructions = [
            "Press F1 to toggle overlay",
            "Press F2 to reset FPS history",
            "Press F3 to toggle fullscreen",
        ]

        for instruction in instructions:
            inst_text = self.small_font.render(instruction, True, (200, 200, 200))
            overlay_surface.blit(inst_text, (10, y_offset))
            y_offset += 15

        # Blit overlay to screen
        self.screen.blit(overlay_surface, (10, 10))

    def reset_fps_history(self) -> None:
        """Reset FPS history."""
        self.fps_history.clear()
        self.frame_count = 0
        self.last_time = time.time()

    def get_fps_info(self) -> dict[str, float]:
        """Get current FPS information."""
        if not self.fps_history:
            return {"current": 0.0, "average": 0.0, "min": 0.0, "max": 0.0}

        current_fps = self.fps_history[-1] if self.fps_history else 0.0
        avg_fps = sum(self.fps_history) / len(self.fps_history)
        min_fps = min(self.fps_history)
        max_fps = max(self.fps_history)

        return {
            "current": current_fps,
            "average": avg_fps,
            "min": min_fps,
            "max": max_fps,
        }
