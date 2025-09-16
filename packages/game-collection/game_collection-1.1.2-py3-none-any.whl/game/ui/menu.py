from __future__ import annotations

import math
import random
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from .scores import ScoreManager


class MainMenu:
    def __init__(self, screen: pygame.Surface, score_manager: ScoreManager) -> None:
        self.screen = screen
        self.score_manager = score_manager
        self.width, self.height = screen.get_size()

        # Цвета
        self.bg_color = (20, 25, 40)
        self.accent_color = (100, 200, 255)
        self.text_color = (255, 255, 255)
        self.hover_color = (150, 220, 255)

        # Шрифты
        pygame.font.init()
        self.title_font = pygame.font.Font(None, 72)
        self.button_font = pygame.font.Font(None, 36)
        self.score_font = pygame.font.Font(None, 24)

        # Игровые опции
        self.games: list[dict[str, str]] = [
            {"name": "Змейка", "key": "snake", "description": "Классическая игра змейка"},
            {"name": "Арканоид", "key": "arkanoid", "description": "Разбей все блоки!"},
            {"name": "Тетрис", "key": "tetris", "description": "Собери линии из фигур"},
            {"name": "Pac-Man", "key": "pacman", "description": "Собери точки, избегай призраков!"},
        ]

        self.selected_game: str | None = None
        self.current_state: str = "main"  # main, scores
        self.hovered_button: int | None = None
        self.hovered_scores: bool = False

        # Анимация частиц
        self.particles: list[dict[str, float]] = []
        self.create_particles()

        # Анимация
        self.time: float = 0

    def create_particles(self) -> None:
        """Создание частиц для фона"""
        for _ in range(50):
            particle = {
                "x": random.randint(0, self.width),
                "y": random.randint(0, self.height),
                "size": random.randint(2, 5),
                "speed": random.uniform(0.5, 2.0),
                "alpha": random.randint(50, 150),
            }
            self.particles.append(particle)

    def update_particles(self, _dt: float) -> None:
        """Обновление частиц"""
        for particle in self.particles:
            particle["y"] -= particle["speed"]
            if particle["y"] < -10:
                particle["y"] = self.height + 10
                particle["x"] = random.randint(0, self.width)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Обработка событий"""
        mouse_pos = pygame.mouse.get_pos()

        # Проверка наведения на кнопки
        self.hovered_button = None
        button_y = 300
        for i, _game in enumerate(self.games):
            button_rect = pygame.Rect(400, button_y + i * 100, 400, 60)
            if button_rect.collidepoint(mouse_pos):
                self.hovered_button = i
                break

        # Проверка наведения на кнопку рекордов
        scores_rect = pygame.Rect(self.width - 200, 50, 150, 40)
        self.hovered_scores = scores_rect.collidepoint(mouse_pos)

        # Обработка кликов
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Левая кнопка мыши
                if self.current_state == "main":
                    if self.hovered_button is not None:
                        self.selected_game = self.games[self.hovered_button]["key"]
                    elif self.hovered_scores:
                        self.current_state = "scores"
                elif self.current_state == "scores":
                    # Кнопка "Назад"
                    back_rect = pygame.Rect(50, 50, 100, 40)
                    if back_rect.collidepoint(mouse_pos):
                        self.current_state = "main"

    def update(self, dt: float) -> None:
        """Обновление меню"""
        self.time += dt
        self.update_particles(dt)

    def draw(self) -> None:
        """Отрисовка меню"""
        if self.current_state == "main":
            self.draw_main_menu()
        elif self.current_state == "scores":
            self.draw_scores()

    def draw_main_menu(self) -> None:
        """Отрисовка главного меню"""
        # Фон с градиентом
        self.screen.fill(self.bg_color)

        # Отрисовка частиц
        for particle in self.particles:
            alpha = int(particle["alpha"])
            color = (*self.accent_color[:2], alpha)
            pygame.draw.circle(
                self.screen, color, (int(particle["x"]), int(particle["y"])), int(particle["size"])
            )

        # Заголовок с анимацией
        title_text = "КОЛЛЕКЦИЯ ИГР"
        title_surface = self.title_font.render(title_text, True, self.text_color)
        title_rect = title_surface.get_rect(center=(self.width // 2, 150))

        # Эффект пульсации для заголовка
        pulse = 1 + 0.1 * math.sin(self.time * 3)
        title_surface = pygame.transform.scale(
            title_surface,
            (int(title_surface.get_width() * pulse), int(title_surface.get_height() * pulse)),
        )
        title_rect = title_surface.get_rect(center=(self.width // 2, 150))

        self.screen.blit(title_surface, title_rect)

        # Подзаголовок
        subtitle_text = "Выберите игру"
        subtitle_surface = self.button_font.render(subtitle_text, True, self.accent_color)
        subtitle_rect = subtitle_surface.get_rect(center=(self.width // 2, 200))
        self.screen.blit(subtitle_surface, subtitle_rect)

        # Кнопки игр
        button_y = 280
        button_width = 400
        button_height = 50
        button_spacing = 80  # Уменьшенный интервал между кнопками
        button_x = (self.width - button_width) // 2  # Центрирование по горизонтали
        for i, game in enumerate(self.games):
            button_rect = pygame.Rect(button_x, button_y + i * button_spacing, button_width, button_height)

            # Цвет кнопки
            if i == self.hovered_button:
                button_color = self.hover_color
                border_color = self.accent_color
            else:
                button_color = (40, 50, 70)
                border_color = (80, 100, 120)

            # Отрисовка кнопки
            pygame.draw.rect(self.screen, button_color, button_rect, border_radius=10)
            pygame.draw.rect(self.screen, border_color, button_rect, 2, border_radius=10)

            # Текст кнопки
            game_text = game["name"]
            game_surface = self.button_font.render(game_text, True, self.text_color)
            game_rect = game_surface.get_rect(center=button_rect.center)
            self.screen.blit(game_surface, game_rect)

            # Описание игры
            desc_surface = self.score_font.render(game["description"], True, self.accent_color)
            desc_rect = desc_surface.get_rect(center=(button_rect.centerx, button_rect.bottom + 15))
            self.screen.blit(desc_surface, desc_rect)

        # Кнопка таблицы рекордов
        scores_rect = pygame.Rect(self.width - 200, 50, 150, 40)
        if self.hovered_scores:
            scores_color = self.hover_color
            border_color = self.accent_color
        else:
            scores_color = (60, 70, 90)
            border_color = self.accent_color

        pygame.draw.rect(self.screen, scores_color, scores_rect, border_radius=5)
        pygame.draw.rect(self.screen, border_color, scores_rect, 2, border_radius=5)

        scores_text = "Рекорды"
        scores_surface = self.score_font.render(scores_text, True, self.text_color)
        scores_text_rect = scores_surface.get_rect(center=scores_rect.center)
        self.screen.blit(scores_surface, scores_text_rect)

        # Инструкции
        instructions = ["ESC - Выход", "Мышь - Выбор игры"]
        for i, instruction in enumerate(instructions):
            inst_surface = self.score_font.render(instruction, True, (150, 150, 150))
            self.screen.blit(inst_surface, (50, self.height - 60 + i * 20))

    def draw_scores(self) -> None:
        """Отрисовка таблицы рекордов"""
        self.screen.fill(self.bg_color)

        # Кнопка "Назад"
        back_rect = pygame.Rect(50, 50, 100, 40)
        pygame.draw.rect(self.screen, (60, 70, 90), back_rect, border_radius=5)
        pygame.draw.rect(self.screen, self.accent_color, back_rect, 2, border_radius=5)

        back_text = "Назад"
        back_surface = self.score_font.render(back_text, True, self.text_color)
        back_text_rect = back_surface.get_rect(center=back_rect.center)
        self.screen.blit(back_surface, back_text_rect)

        # Заголовок
        title_text = "ТАБЛИЦА РЕКОРДОВ"
        title_surface = self.title_font.render(title_text, True, self.text_color)
        title_rect = title_surface.get_rect(center=(self.width // 2, 120))
        self.screen.blit(title_surface, title_rect)

        # Рекорды для каждой игры
        y_offset = 200
        for game in self.games:
            game_name = game["name"]
            scores = self.score_manager.get_scores(game["key"])

            # Название игры
            game_title_surface = self.button_font.render(game_name, True, self.accent_color)
            game_title_rect = game_title_surface.get_rect(center=(self.width // 2, y_offset))
            self.screen.blit(game_title_surface, game_title_rect)

            # Рекорды
            if scores:
                for i, score in enumerate(scores[:5]):  # Топ 5
                    score_text = f"{i + 1}. {score['player']}: {score['score']}"
                    score_surface = self.score_font.render(score_text, True, self.text_color)
                    score_rect = score_surface.get_rect(
                        center=(self.width // 2, y_offset + 40 + i * 25)
                    )
                    self.screen.blit(score_surface, score_rect)
            else:
                no_scores_text = "Рекордов пока нет"
                no_scores_surface = self.score_font.render(no_scores_text, True, (150, 150, 150))
                no_scores_rect = no_scores_surface.get_rect(center=(self.width // 2, y_offset + 40))
                self.screen.blit(no_scores_surface, no_scores_rect)

            y_offset += 200

    def get_selected_game(self) -> str | None:
        """Получить выбранную игру"""
        return self.selected_game

    def reset_selection(self) -> None:
        """Сброс выбора"""
        self.selected_game = None
