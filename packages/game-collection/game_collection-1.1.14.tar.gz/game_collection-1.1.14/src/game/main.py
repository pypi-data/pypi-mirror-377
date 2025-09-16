from __future__ import annotations

import sys

import pygame

from .config import config
from .debug_overlay import DebugOverlay
from .games.arkanoid import ArkanoidGame
from .games.pacman import PacmanGame
from .games.snake import SnakeGame
from .games.tetris import TetrisGame
from .ui.menu import MainMenu
from .ui.scores import ScoreManager


class GameCollection:
    def __init__(self) -> None:
        pygame.init()

        # Get display configuration
        display_config = config.get_display_config()
        width = display_config.get("width", 1024)
        height = display_config.get("height", 768)
        fullscreen = display_config.get("fullscreen", False)

        # Set up display
        if fullscreen:
            self.screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((width, height))

        pygame.display.set_caption("Game Collection")
        self.clock = pygame.time.Clock()
        self.running = True

        # Инициализация меню и системы рекордов
        self.score_manager = ScoreManager()
        self.menu = MainMenu(self.screen, self.score_manager)

        # Debug overlay
        self.debug_overlay = DebugOverlay(self.screen, config)

        # Текущее состояние
        self.current_game: SnakeGame | ArkanoidGame | TetrisGame | PacmanGame | None = None
        self.current_state: str = "menu"  # menu, game, scores

    def run(self) -> None:
        display_config = config.get_display_config()
        fps = display_config.get("fps", 60)

        while self.running:
            dt = self.clock.tick(fps) / 1000.0
            events = pygame.event.get()

            # Update debug overlay
            self.debug_overlay.update_fps(dt)
            self.debug_overlay.update_status(self.current_state, self.get_game_name())
            self.debug_overlay.update_input(pygame.mouse.get_pos(), self.get_pressed_keys())

            # Обработка глобальных событий
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.current_state == "game":
                            self.return_to_menu()
                        elif self.current_state == "scores":
                            self.current_state = "menu"
                        else:
                            self.running = False
                    elif event.key == pygame.K_F1:
                        self.debug_overlay.toggle()
                    elif event.key == pygame.K_F2:
                        self.debug_overlay.reset_fps_history()
                    elif event.key == pygame.K_F3:
                        self.toggle_fullscreen()

            # Обновление и отрисовка
            if self.current_state == "menu":
                self.menu.handle_events(events)
                self.menu.update(dt)
                self.menu.draw()

                # Проверка выбора игры
                selected_game = self.menu.get_selected_game()
                if selected_game:
                    self.start_game(selected_game)

            elif self.current_state == "game" and self.current_game:
                self.current_game.handle_events(events)
                self.current_game.update(dt)
                self.current_game.draw()

                # Проверка окончания игры
                if self.current_game.is_game_over():
                    score = self.current_game.get_score()
                    game_name = self.current_game.get_game_name()
                    self.score_manager.add_score(game_name, score)
                    self.return_to_menu()

            elif self.current_state == "scores":
                self.menu.draw_scores()

            # Draw debug overlay
            self.debug_overlay.draw()

            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def start_game(self, game_name: str) -> None:
        """Запуск выбранной игры"""
        if game_name == "snake":
            self.current_game = SnakeGame(self.screen)
        elif game_name == "arkanoid":
            self.current_game = ArkanoidGame(self.screen)
        elif game_name == "tetris":
            self.current_game = TetrisGame(self.screen)
        elif game_name == "pacman":
            self.current_game = PacmanGame(self.screen)

        self.current_state = "game"

    def return_to_menu(self) -> None:
        """Возврат в главное меню"""
        self.current_game = None
        self.current_state = "menu"
        self.menu.reset_selection()

    def get_game_name(self) -> str:
        """Get current game name for debug overlay."""
        if self.current_game:
            return self.current_game.get_game_name()
        return "Menu"

    def get_pressed_keys(self) -> list[str]:
        """Get currently pressed keys for debug overlay."""
        keys = pygame.key.get_pressed()
        pressed_keys = []

        key_mapping = {
            pygame.K_UP: "UP",
            pygame.K_DOWN: "DOWN",
            pygame.K_LEFT: "LEFT",
            pygame.K_RIGHT: "RIGHT",
            pygame.K_SPACE: "SPACE",
            pygame.K_RETURN: "ENTER",
            pygame.K_ESCAPE: "ESC",
            pygame.K_F1: "F1",
            pygame.K_F2: "F2",
            pygame.K_F3: "F3",
        }

        for key_code, key_name in key_mapping.items():
            if keys[key_code]:
                pressed_keys.append(key_name)

        return pressed_keys

    def toggle_fullscreen(self) -> None:
        """Toggle fullscreen mode."""
        display_config = config.get_display_config()
        width = display_config.get("width", 1024)
        height = display_config.get("height", 768)

        if self.screen.get_flags() & pygame.FULLSCREEN:
            # Switch to windowed mode
            self.screen = pygame.display.set_mode((width, height))
            config.set("display.fullscreen", False)
        else:
            # Switch to fullscreen mode
            self.screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
            config.set("display.fullscreen", True)

        config.save_config()

        # Update debug overlay with new screen
        self.debug_overlay.screen = self.screen


def main() -> None:
    """Main entry point for the game collection."""
    game = GameCollection()
    game.run()


if __name__ == "__main__":
    main()
