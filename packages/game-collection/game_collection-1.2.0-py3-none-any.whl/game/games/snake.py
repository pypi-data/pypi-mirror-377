from __future__ import annotations

import math
import random
from typing import Any

import pygame

from .base import BaseGame


class SnakeGame(BaseGame):
    def __init__(self, screen: pygame.Surface) -> None:
        super().__init__(screen)
        self.width, self.height = screen.get_size()

        # Игровое поле
        self.grid_size = 20
        self.grid_width = self.width // self.grid_size
        self.grid_height = self.height // self.grid_size

        # Цвета
        self.bg_color = (20, 25, 40)
        self.snake_color = (100, 200, 100)
        self.food_color = (255, 100, 100)
        self.bomb_color = (50, 50, 50)  # Черные бомбы
        self.golden_apple_color = (255, 215, 0)  # Золотые яблоки
        self.text_color = (255, 255, 255)

        # Шрифты
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Инициализация переменных бомб
        self.bomb: tuple[int, int] | None = None
        self.apples_since_bomb: int = 0
        self.bomb_timer: float = 0.0
        self.bomb_redness: float = 0.0  # Уровень покраснения бомбы (0-1)
        self.bomb_target: int = random.randint(4, 6)  # Случайный интервал 4-6 яблок

        # Инициализация переменных золотых яблок
        self.golden_apple: tuple[int, int] | None = None
        self.apples_since_golden: int = 0
        self.golden_apple_timer: float = 0.0
        self.golden_apple_target: int = random.randint(4, 6)  # Случайный интервал 4-6 яблок
        self.score_animations: list[dict[str, Any]] = []  # Анимации +10 очков

        # Инициализация переменных анимации взрыва
        self.explosion_animations: list[dict[str, Any]] = []  # Анимации взрывов бомб

        # Инициализация игры
        self.reset_game()

        # Состояние игры
        self.game_over: bool = False
        self.paused: bool = False

    def reset_game(self) -> None:
        """Сброс игры"""
        # Змейка начинается в центре с длиной 3 клетки
        center_x = self.grid_width // 2
        center_y = self.grid_height // 2
        self.snake: list[tuple[int, int]] = [
            (center_x, center_y),
            (center_x - 1, center_y),
            (center_x - 2, center_y),
        ]
        self.direction: tuple[int, int] = (1, 0)  # Движение вправо
        self.next_direction: tuple[int, int] = (1, 0)

        # Еда
        self.food: tuple[int, int] | None = self.generate_food()
        self.bomb = None  # Бомба
        self.apples_since_bomb = 0  # Счетчик яблок с последней бомбы

        # Счет и уровень
        self.score: int = 0
        self.level: int = 1
        self.apples_eaten: int = 0
        self.game_over = False
        self.paused = False
        self.move_timer: float = 0
        self.base_speed: float = 0.15  # Базовая скорость
        self.current_speed: float = self.base_speed
        self.level_up_timer: float = 0  # Таймер для показа уведомления о повышении уровня

    def generate_food(self) -> tuple[int, int] | None:
        """Генерация еды"""
        attempts = 0
        while attempts < 100:  # Ограничиваем количество попыток
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
            if (x, y) not in self.snake and (x, y) != self.bomb and (x, y) != self.golden_apple:
                return (x, y)
            attempts += 1

        # Если не удалось найти свободное место, возвращаем None
        print("Предупреждение: не удалось найти свободное место для еды")
        return None

    def generate_bomb(self) -> tuple[int, int]:
        """Генерация бомбы"""
        while True:
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
            if (x, y) not in self.snake and (x, y) != self.food and (x, y) != self.golden_apple:
                return (x, y)

    def generate_golden_apple(self) -> tuple[int, int]:
        """Генерация золотого яблока"""
        while True:
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
            if (x, y) not in self.snake and (x, y) != self.food and (x, y) != self.bomb:
                return (x, y)

    def create_explosion_animation(self, bomb_pos: tuple[int, int]) -> None:
        """Создание анимации взрыва бомбы"""
        bomb_x = bomb_pos[0] * self.grid_size + self.grid_size // 2
        bomb_y = bomb_pos[1] * self.grid_size + self.grid_size // 2

        # Создаем несколько частиц взрыва
        for i in range(8):
            angle = (i * 45) * 3.14159 / 180  # 45 градусов между частицами
            speed = random.uniform(50, 100)
            self.explosion_animations.append(
                {
                    "x": bomb_x,
                    "y": bomb_y,
                    "vx": speed * math.cos(angle),
                    "vy": speed * math.sin(angle),
                    "timer": 1.0,
                    "alpha": 255,
                    "size": random.randint(3, 8),
                }
            )

    def handle_events(self, events: list[pygame.event.Event] | None = None) -> None:
        """Обработка событий"""
        if events is None:
            events = pygame.event.get()

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and self.direction != (0, 1):
                    self.next_direction = (0, -1)
                elif event.key == pygame.K_DOWN and self.direction != (0, -1):
                    self.next_direction = (0, 1)
                elif event.key == pygame.K_LEFT and self.direction != (1, 0):
                    self.next_direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and self.direction != (-1, 0):
                    self.next_direction = (1, 0)
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()

    def update(self, dt: float) -> None:
        """Обновление игры"""
        if self.game_over or self.paused:
            return

        # Обновление общего времени для анимаций
        if not hasattr(self, "time"):
            self.time = 0.0
        self.time += dt

        # Обновление таймера уведомления о повышении уровня
        if self.level_up_timer > 0:
            self.level_up_timer -= dt

        # Обновление таймера бомбы
        if self.bomb and self.bomb_timer > 0:
            self.bomb_timer -= dt

            # Расчет покраснения бомбы (0-1, где 1 = полное покраснение)
            total_time = 10.0  # Общее время жизни бомбы
            self.bomb_redness = 1.0 - (self.bomb_timer / total_time)

            if self.bomb_timer <= 0:
                # Бомба взрывается и исчезает
                bomb_pos = self.bomb  # Сохраняем позицию для анимации
                self.create_explosion_animation(bomb_pos)
                self.bomb = None
                self.bomb_timer = 0
                self.bomb_redness = 0.0

        # Обновление таймера золотого яблока
        if self.golden_apple and self.golden_apple_timer > 0:
            self.golden_apple_timer -= dt
            if self.golden_apple_timer <= 0:
                # Золотое яблоко гниет и исчезает
                self.golden_apple = None
                self.golden_apple_timer = 0

        # Обновление анимаций +10 очков
        for animation in self.score_animations[:]:
            animation["timer"] -= dt
            animation["y"] -= dt * 30  # Поднимается вверх
            animation["alpha"] = max(0, int(255 * (animation["timer"] / 2.0)))
            if animation["timer"] <= 0:
                self.score_animations.remove(animation)

        # Обновление анимаций взрыва
        for animation in self.explosion_animations[:]:
            animation["timer"] -= dt
            animation["x"] += animation["vx"] * dt
            animation["y"] += animation["vy"] * dt
            animation["alpha"] = max(0, int(255 * (animation["timer"] / 1.0)))
            animation["size"] = max(1, int(animation["size"] * (animation["timer"] / 1.0)))
            if animation["timer"] <= 0:
                self.explosion_animations.remove(animation)

        # Замедление змейки
        self.move_timer += dt
        if self.move_timer < self.current_speed:  # Движение с текущей скоростью
            return

        self.move_timer = 0

        # Обновление направления
        self.direction = self.next_direction

        # Движение змейки
        head_x, head_y = self.snake[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])

        # Проверка столкновения со стенами
        if (
            new_head[0] < 0
            or new_head[0] >= self.grid_width
            or new_head[1] < 0
            or new_head[1] >= self.grid_height
        ):
            self.game_over = True
            # Звук столкновения со стеной
            self.sound_manager.play_sound("snake_crash")
            return

        # Проверка столкновения с собой
        if new_head in self.snake:
            self.game_over = True
            # Звук столкновения с собой
            self.sound_manager.play_sound("snake_crash")
            return

        # Добавление новой головы
        self.snake.insert(0, new_head)

        # Звук движения змейки
        self.sound_manager.play_sound("snake_move", 0.3)  # Тихий звук движения

        # Проверка поедания бомбы
        if self.bomb and new_head == self.bomb:
            self.game_over = True
            # Звук взрыва
            self.sound_manager.play_sound("snake_crash")
            return

        # Проверка поедания золотого яблока
        if self.golden_apple and new_head == self.golden_apple:
            self.score += 10
            self.apples_eaten += 1
            self.apples_since_bomb += 1
            self.apples_since_golden += 1

            # Звук поедания золотого яблока
            self.sound_manager.play_sound("snake_eat")

            # Анимация +10 очков
            head_x = new_head[0] * self.grid_size + self.grid_size // 2
            head_y = new_head[1] * self.grid_size + self.grid_size // 2
            self.score_animations.append({"x": head_x, "y": head_y, "timer": 2.0, "alpha": 255})

            # Удаление золотого яблока
            self.golden_apple = None
            self.golden_apple_timer = 0

            # Проверка повышения уровня
            new_level = (self.apples_eaten // 10) + 1
            if new_level > self.level:
                self.level = new_level
                self.current_speed = max(0.05, self.base_speed - (self.level - 1) * 0.01)
                self.level_up_timer = 2.0

            # Генерация бомбы через случайный интервал 4-6 яблок
            if self.apples_since_bomb >= self.bomb_target:
                self.bomb = self.generate_bomb()
                self.bomb_timer = 10.0
                self.bomb_redness = 0.0  # Сброс покраснения
                self.apples_since_bomb = 0
                self.bomb_target = random.randint(4, 6)  # Новый случайный интервал

            # Генерация золотого яблока через случайный интервал 4-6 яблок
            if self.apples_since_golden >= self.golden_apple_target:
                self.golden_apple = self.generate_golden_apple()
                self.golden_apple_timer = 8.0  # Золотое яблоко гниет через 8 секунд
                self.apples_since_golden = 0
                self.golden_apple_target = random.randint(4, 6)  # Новый случайный интервал

        # Проверка поедания обычной еды
        elif new_head == self.food:
            self.score += 10
            self.apples_eaten += 1
            self.apples_since_bomb += 1
            self.apples_since_golden += 1

            # Звук поедания еды
            self.sound_manager.play_sound("snake_eat")

            # Проверка повышения уровня
            new_level = (self.apples_eaten // 10) + 1
            if new_level > self.level:
                self.level = new_level
                # Ускорение змейки (уменьшение времени между движениями)
                self.current_speed = max(0.05, self.base_speed - (self.level - 1) * 0.01)
                # Показать уведомление о повышении уровня
                self.level_up_timer = 2.0  # Показать 2 секунды

            # Генерация новой еды
            new_food = self.generate_food()
            if new_food is not None:
                self.food = new_food

            # Генерация бомбы каждые 5 яблок
            if self.apples_since_bomb >= 5:
                self.bomb = self.generate_bomb()
                self.bomb_timer = 10.0  # Бомба взрывается через 10 секунд
                self.apples_since_bomb = 0

            # Генерация золотого яблока через случайный интервал 4-6 яблок
            if self.apples_since_golden >= self.golden_apple_target:
                self.golden_apple = self.generate_golden_apple()
                self.golden_apple_timer = 8.0  # Золотое яблоко гниет через 8 секунд
                self.apples_since_golden = 0
                self.golden_apple_target = random.randint(4, 6)  # Новый случайный интервал
        else:
            # Удаление хвоста, если еда не съедена
            self.snake.pop()

    def draw(self) -> None:
        """Отрисовка игры"""
        self.screen.fill(self.bg_color)

        if not self.game_over:
            # Отрисовка змейки
            for i, segment in enumerate(self.snake):
                x = segment[0] * self.grid_size
                y = segment[1] * self.grid_size

                # Голова змейки
                if i == 0:
                    pygame.draw.rect(
                        self.screen, self.snake_color, (x, y, self.grid_size, self.grid_size)
                    )
                    pygame.draw.rect(
                        self.screen, (255, 255, 255), (x, y, self.grid_size, self.grid_size), 2
                    )
                else:
                    # Тело змейки
                    pygame.draw.rect(
                        self.screen,
                        self.snake_color,
                        (x + 2, y + 2, self.grid_size - 4, self.grid_size - 4),
                    )

            # Отрисовка еды
            if self.food is not None:
                food_x = self.food[0] * self.grid_size
                food_y = self.food[1] * self.grid_size
                pygame.draw.rect(
                    self.screen, self.food_color, (food_x, food_y, self.grid_size, self.grid_size)
                )
                pygame.draw.rect(
                    self.screen,
                    (255, 255, 255),
                    (food_x, food_y, self.grid_size, self.grid_size),
                    2,
                )

            # Отрисовка бомбы
            if self.bomb:
                bomb_x = self.bomb[0] * self.grid_size
                bomb_y = self.bomb[1] * self.grid_size
                center_x = bomb_x + self.grid_size // 2
                center_y = bomb_y + self.grid_size // 2
                radius = self.grid_size // 2 - 2

                # Расчет цвета бомбы с учетом покраснения
                base_color = self.bomb_color  # Черный цвет
                red_color = (255, 0, 0)  # Красный цвет

                # Интерполяция между черным и красным
                bomb_color = (
                    int(base_color[0] + (red_color[0] - base_color[0]) * self.bomb_redness),
                    int(base_color[1] + (red_color[1] - base_color[1]) * self.bomb_redness),
                    int(base_color[2] + (red_color[2] - base_color[2]) * self.bomb_redness),
                )

                # Пульсация бомбы перед взрывом
                pulse_factor = 1.0
                if self.bomb_redness > 0.7:  # Пульсация в последние 3 секунды
                    pulse_intensity = (self.bomb_redness - 0.7) / 0.3  # 0-1
                    pulse_factor = 1.0 + 0.2 * pulse_intensity * math.sin(self.time * 10)

                # Основной корпус бомбы (постепенно краснеет и пульсирует)
                pulse_radius = int(radius * pulse_factor)
                pygame.draw.circle(self.screen, bomb_color, (center_x, center_y), pulse_radius)

                # Рамка бомбы (тоже краснеет и пульсирует)
                border_color = (
                    int(100 + (255 - 100) * self.bomb_redness),
                    int(100 + (0 - 100) * self.bomb_redness),
                    int(100 + (0 - 100) * self.bomb_redness),
                )
                pygame.draw.circle(self.screen, border_color, (center_x, center_y), pulse_radius, 2)

                # Фитиль (светящиеся точки)
                fuse_x = center_x + radius - 3
                fuse_y = center_y - radius + 5

                # Светящиеся точки фитиля (становятся ярче при покраснении)
                sparkle_intensity = min(1.5, 1.0 + self.bomb_redness * 0.5)  # Ограничиваем до 1.5
                sparkle_colors = [
                    (
                        min(255, int(255 * sparkle_intensity)),
                        min(255, int(255 * sparkle_intensity)),
                        0,
                    ),
                    (
                        min(255, int(255 * sparkle_intensity)),
                        min(255, int(200 * sparkle_intensity)),
                        0,
                    ),
                    (
                        min(255, int(255 * sparkle_intensity)),
                        min(255, int(150 * sparkle_intensity)),
                        0,
                    ),
                ]
                for i in range(3):
                    sparkle_x = fuse_x + i * 2
                    sparkle_y = fuse_y - i * 2
                    pygame.draw.circle(
                        self.screen, sparkle_colors[i % 3], (sparkle_x, sparkle_y), 2
                    )

                # Линия фитиля
                pygame.draw.line(
                    self.screen,
                    (150, 100, 50),
                    (center_x + radius - 5, center_y - radius + 3),
                    (fuse_x + 4, fuse_y - 4),
                    2,
                )

                # Взрывчатые полоски на бомбе (становятся краснее)
                stripe_color = (
                    int(200 + (255 - 200) * self.bomb_redness),
                    int(200 + (100 - 200) * self.bomb_redness),
                    int(200 + (100 - 200) * self.bomb_redness),
                )
                pygame.draw.line(
                    self.screen,
                    stripe_color,
                    (center_x - 4, center_y - 2),
                    (center_x + 4, center_y + 2),
                    1,
                )
                pygame.draw.line(
                    self.screen,
                    stripe_color,
                    (center_x - 2, center_y - 4),
                    (center_x + 2, center_y + 4),
                    1,
                )

            # Отрисовка золотого яблока
            if self.golden_apple:
                golden_x = self.golden_apple[0] * self.grid_size
                golden_y = self.golden_apple[1] * self.grid_size
                center_x = golden_x + self.grid_size // 2
                center_y = golden_y + self.grid_size // 2
                radius = self.grid_size // 2 - 2

                # Определяем цвет в зависимости от времени до гниения
                if self.golden_apple_timer > 4:
                    # Свежее золотое яблоко
                    apple_color = self.golden_apple_color
                    border_color = (255, 255, 0)
                elif self.golden_apple_timer > 2:
                    # Начинает портиться
                    apple_color = (200, 150, 0)
                    border_color = (150, 100, 0)
                else:
                    # Почти сгнило
                    apple_color = (100, 50, 0)
                    border_color = (50, 25, 0)

                # Основное яблоко
                pygame.draw.circle(self.screen, apple_color, (center_x, center_y), radius)
                pygame.draw.circle(self.screen, border_color, (center_x, center_y), radius, 2)

                # Блеск на золотом яблоке
                if self.golden_apple_timer > 4:
                    pygame.draw.circle(
                        self.screen, (255, 255, 255), (center_x - 3, center_y - 3), 2
                    )

            # Отрисовка анимаций +10 очков
            for animation in self.score_animations:
                if animation["alpha"] > 0:
                    # Создаем поверхность с прозрачностью
                    score_surface = self.small_font.render("+10", True, (255, 255, 0))
                    score_surface.set_alpha(animation["alpha"])
                    score_rect = score_surface.get_rect(center=(animation["x"], animation["y"]))
                    self.screen.blit(score_surface, score_rect)

            # Отрисовка анимаций взрыва
            for animation in self.explosion_animations:
                if animation["alpha"] > 0:
                    # Создаем поверхность для частицы взрыва
                    particle_surface = pygame.Surface(
                        (animation["size"] * 2, animation["size"] * 2), pygame.SRCALPHA
                    )
                    # Цвет частицы меняется от красного к оранжевому
                    color_ratio = animation["timer"] / 1.0
                    particle_color = (
                        int(255 * color_ratio + 255 * (1 - color_ratio)),
                        int(100 * color_ratio + 200 * (1 - color_ratio)),
                        int(0 * color_ratio + 100 * (1 - color_ratio)),
                    )
                    pygame.draw.circle(
                        particle_surface,
                        particle_color,
                        (animation["size"], animation["size"]),
                        animation["size"],
                    )
                    particle_surface.set_alpha(animation["alpha"])

                    # Позиционируем частицу
                    particle_rect = particle_surface.get_rect(
                        center=(animation["x"], animation["y"])
                    )
                    self.screen.blit(particle_surface, particle_rect)

        # Отрисовка интерфейса
        self.draw_ui()

    def draw_ui(self) -> None:
        """Отрисовка пользовательского интерфейса"""
        # Счет
        score_text = f"Счет: {self.score}"
        score_surface = self.font.render(score_text, True, self.text_color)
        self.screen.blit(score_surface, (10, 10))

        # Уровень
        level_text = f"Уровень: {self.level}"
        level_surface = self.font.render(level_text, True, self.text_color)
        self.screen.blit(level_surface, (10, 50))

        # Длина змейки
        # length_text = f"Длина: {len(self.snake)}"
        # length_surface = self.small_font.render(length_text, True, self.text_color)
        # self.screen.blit(length_surface, (10, 90))

        # Съеденные яблоки
        # apples_text = f"Яблоки: {self.apples_eaten}"
        # apples_surface = self.small_font.render(apples_text, True, self.text_color)
        # self.screen.blit(apples_surface, (10, 115))

        # Информация о бомбах
        if self.bomb:
            bomb_text = "БОМБА НА ПОЛЕ!"
            bomb_surface = self.small_font.render(bomb_text, True, (255, 100, 100))
            self.screen.blit(bomb_surface, (10, 140))

            # Время до взрыва
            time_left = max(0, int(self.bomb_timer))
            timer_text = f"Взрыв через: {time_left}с"
            timer_color = (255, 100, 100) if time_left <= 3 else (255, 200, 100)
            timer_surface = self.small_font.render(timer_text, True, timer_color)
            self.screen.blit(timer_surface, (10, 165))
        # else:
        # bomb_text = f"До бомбы: {self.bomb_target - self.apples_since_bomb}"
        # bomb_surface = self.small_font.render(bomb_text, True, (200, 200, 200))
        # self.screen.blit(bomb_surface, (10, 140))

        # Информация о золотых яблоках
        if self.golden_apple:
            golden_text = "ЗОЛОТОЕ ЯБЛОКО!"
            golden_surface = self.small_font.render(golden_text, True, (255, 215, 0))
            self.screen.blit(golden_surface, (10, 190))

            # Время до гниения
            time_left = max(0, int(self.golden_apple_timer))
            timer_text = f"Гниет через: {time_left}с"
            timer_color = (255, 100, 100) if time_left <= 2 else (255, 215, 0)
            timer_surface = self.small_font.render(timer_text, True, timer_color)
            self.screen.blit(timer_surface, (10, 215))
        # else:
        # golden_text = f"До золотого: {self.golden_apple_target - self.apples_since_golden}"
        # golden_surface = self.small_font.render(golden_text, True, (200, 200, 200))
        # self.screen.blit(golden_surface, (10, 190))

        # Состояние игры
        if self.game_over:
            game_over_text = "ИГРА ОКОНЧЕНА!"
            game_over_surface = self.font.render(game_over_text, True, (255, 100, 100))
            game_over_rect = game_over_surface.get_rect(
                center=(self.width // 2, self.height // 2 - 50)
            )
            self.screen.blit(game_over_surface, game_over_rect)

            restart_text = "Нажмите R для перезапуска"
            restart_surface = self.small_font.render(restart_text, True, self.text_color)
            restart_rect = restart_surface.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(restart_surface, restart_rect)

            esc_text = "ESC - Выход в меню"
            esc_surface = self.small_font.render(esc_text, True, self.text_color)
            esc_rect = esc_surface.get_rect(center=(self.width // 2, self.height // 2 + 30))
            self.screen.blit(esc_surface, esc_rect)

        elif self.paused:
            pause_text = "ПАУЗА"
            pause_surface = self.font.render(pause_text, True, self.text_color)
            pause_rect = pause_surface.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(pause_surface, pause_rect)

            space_text = "Пробел - Продолжить"
            space_surface = self.small_font.render(space_text, True, self.text_color)
            space_rect = space_surface.get_rect(center=(self.width // 2, self.height // 2 + 40))
            self.screen.blit(space_surface, space_rect)

        # Уведомление о повышении уровня
        if self.level_up_timer > 0:
            level_up_text = f"УРОВЕНЬ {self.level}!"
            level_up_surface = self.font.render(level_up_text, True, (100, 255, 100))
            level_up_rect = level_up_surface.get_rect(
                center=(self.width // 2, self.height // 2 - 100)
            )
            self.screen.blit(level_up_surface, level_up_rect)

            speed_text = "Скорость увеличена!"
            speed_surface = self.small_font.render(speed_text, True, (100, 255, 100))
            speed_rect = speed_surface.get_rect(center=(self.width // 2, self.height // 2 - 70))
            self.screen.blit(speed_surface, speed_rect)

        # Управление
        controls = [
            "Стрелки - Движение",
            "Пробел - Пауза",
            "ESC - Выход",
        ]
        for i, control in enumerate(controls):
            control_surface = self.small_font.render(control, True, (150, 150, 150))
            self.screen.blit(control_surface, (self.width - 200, 10 + i * 25))

    def is_game_over(self) -> bool:
        """Проверка окончания игры"""
        return self.game_over

    def get_score(self) -> int:
        """Получение счета"""
        return self.score

    def get_game_name(self) -> str:
        """Получение названия игры"""
        return "snake"
