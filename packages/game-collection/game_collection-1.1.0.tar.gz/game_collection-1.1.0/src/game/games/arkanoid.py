from __future__ import annotations

import math
import random
from typing import Any

import pygame

from games.base import BaseGame


class ArkanoidGame(BaseGame):
    def __init__(self, screen: pygame.Surface) -> None:
        super().__init__(screen)
        self.width, self.height = screen.get_size()

        # Цвета
        self.bg_color: tuple[int, int, int] = (20, 25, 40)
        self.paddle_color: tuple[int, int, int] = (100, 200, 255)
        self.ball_color: tuple[int, int, int] = (255, 255, 255)
        self.block_colors: list[tuple[int, int, int]] = [
            (255, 100, 100),  # Красный
            (255, 200, 100),  # Оранжевый
            (255, 255, 100),  # Желтый
            (100, 255, 100),  # Зеленый
            (100, 200, 255),  # Синий
            (200, 100, 255),  # Фиолетовый
        ]
        self.text_color: tuple[int, int, int] = (255, 255, 255)

        # Шрифты
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Инициализация игры
        self.reset_game()

        # Состояние игры
        self.game_over: bool = False
        self.paused: bool = False
        self.level_complete: bool = False

    def reset_game(self) -> None:
        """Сброс игры"""
        # Платформа
        self.paddle_width: int = 100
        self.paddle_height: int = 15
        self.paddle_x: float = self.width // 2 - self.paddle_width // 2
        self.paddle_y: float = self.height - 50
        self.paddle_speed: int = 8

        # Мяч
        self.ball_radius: int = 8
        self.ball_x: float = self.width // 2
        self.ball_y: float = self.paddle_y - self.ball_radius - 5
        self.ball_speed_x: float = random.choice([-5, 5])
        self.ball_speed_y: float = -5
        self.ball_speed: float = 5
        self.max_ball_speed: float = 8  # Максимальная скорость мяча

        # Система прогрессивного увеличения скорости
        self.target_ball_speed: float = 5  # Установленная скорость мяча
        self.speed_increase_timer: float = 0.0  # Таймер для увеличения скорости
        self.speed_increase_interval: float = 20.0  # Интервал увеличения скорости (20 секунд)

        # Счет и жизни
        self.score: int = 0
        self.lives: int = 3
        self.level: int = 1
        self.game_over = False
        self.paused = False
        self.level_complete = False

        # Ракеты
        self.rockets: list[dict[str, Any]] = []
        self.rocket_speed: int = 3
        self.rocket_width: int = 12
        self.rocket_height: int = 40

        # Дополнительные мячи
        self.extra_balls: list[dict[str, Any]] = []

        # Блоки (создаем после инициализации level)
        self.create_blocks()

    def create_blocks(self) -> None:
        """Создание блоков со случайным расположением"""
        self.blocks: list[dict[str, Any]] = []
        block_width = 80
        block_height = 30
        rows = 6
        cols = self.width // (block_width + 5)

        start_x = (self.width - cols * (block_width + 5) + 5) // 2
        start_y = 100

        # Разные паттерны для разных уровней
        patterns = [
            "random",  # Полностью случайный
            "pyramid",  # Пирамида
            "checker",  # Шахматный порядок
            "lines",  # Горизонтальные линии
            "sparse",  # Редкое расположение
        ]

        pattern = patterns[(self.level - 1) % len(patterns)]

        for row in range(rows):
            for col in range(cols):
                should_create = False

                if pattern == "random":
                    # Полностью случайное расположение
                    should_create = random.random() < 0.7
                elif pattern == "pyramid":
                    # Пирамида - больше блоков в центре
                    center_col = cols // 2
                    distance_from_center = abs(col - center_col)
                    max_distance = cols // 2
                    probability = 1.0 - (distance_from_center / max_distance) * 0.5
                    should_create = random.random() < probability
                elif pattern == "checker":
                    # Шахматный порядок
                    should_create = (row + col) % 2 == 0
                elif pattern == "lines":
                    # Горизонтальные линии с пропусками
                    should_create = row % 2 == 0 and random.random() < 0.8
                elif pattern == "sparse":
                    # Редкое расположение
                    should_create = random.random() < 0.4

                if should_create:
                    x = start_x + col * (block_width + 5)
                    y = start_y + row * (block_height + 5)

                    # Случайный цвет из доступных
                    color_index = random.randint(0, len(self.block_colors) - 1)

                    # Случайные очки (10-60)
                    points = random.randint(10, 60)

                    # Специальные блоки с большими очками (5% вероятность)
                    if random.random() < 0.05:
                        points = random.randint(100, 200)
                        color_index = 0  # Красный для специальных блоков

                    block = {
                        "rect": pygame.Rect(x, y, block_width, block_height),
                        "color": self.block_colors[color_index],
                        "points": points,
                        "destroyed": False,
                    }
                    self.blocks.append(block)

    def handle_events(self, events: list[pygame.event.Event] | None = None) -> None:
        """Обработка событий"""
        if events is None:
            events = pygame.event.get()

        keys = pygame.key.get_pressed()

        if not self.game_over and not self.paused and not self.level_complete:
            # Движение платформы
            if keys[pygame.K_LEFT] and self.paddle_x > 0:
                self.paddle_x -= self.paddle_speed
            if keys[pygame.K_RIGHT] and self.paddle_x < self.width - self.paddle_width:
                self.paddle_x += self.paddle_speed

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.paused:
                        self.paused = False
                    elif self.level_complete:
                        self.next_level()
                    elif self.game_over:
                        self.reset_game()
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()

    def update(self, dt: float) -> None:
        """Обновление игры"""
        if self.game_over or self.paused or self.level_complete:
            return

        # Определение прямоугольника платформы для всех проверок
        paddle_rect = pygame.Rect(
            self.paddle_x, self.paddle_y, self.paddle_width, self.paddle_height
        )

        # Обновление таймера увеличения скорости
        self.speed_increase_timer += dt
        if self.speed_increase_timer >= self.speed_increase_interval:
            self.speed_increase_timer = 0.0
            if self.target_ball_speed < self.max_ball_speed:
                self.target_ball_speed += 0.5  # Увеличиваем установленную скорость на 0.5

        # Проверка столкновения с блоками ПЕРЕД движением
        self.check_block_collisions()

        # Обновление позиции мяча
        self.ball_x += self.ball_speed_x
        self.ball_y += self.ball_speed_y

        # Отскок от стен
        if self.ball_x <= self.ball_radius or self.ball_x >= self.width - self.ball_radius:
            self.ball_speed_x = -self.ball_speed_x
        if self.ball_y <= self.ball_radius:
            self.ball_speed_y = -self.ball_speed_y

        # Обновление ракет
        rockets_to_remove = []
        for i, rocket in enumerate(self.rockets):
            rocket["y"] += self.rocket_speed
            rocket["flame_timer"] += dt * 10  # Анимация пламени

            # Проверка столкновения с платформой
            rocket_rect = pygame.Rect(
                rocket["x"], rocket["y"], self.rocket_width, self.rocket_height
            )

            if rocket_rect.colliderect(paddle_rect):
                self.lives -= 1
                rockets_to_remove.append(i)
                if self.lives <= 0:
                    self.game_over = True
                else:
                    # Перезапуск мяча
                    self.ball_x = self.width // 2
                    self.ball_y = self.paddle_y - self.ball_radius - 5
                    self.ball_speed_x = random.choice([-5, 5])
                    self.ball_speed_y = -5

            # Удаление ракет, упавших за экран
            elif rocket["y"] > self.height:
                rockets_to_remove.append(i)

        # Удаление ракет
        for i in reversed(rockets_to_remove):
            self.rockets.pop(i)

        # Обновление дополнительных мячей
        for ball in self.extra_balls:
            # Движение мяча
            ball["x"] += ball["speed_x"]
            ball["y"] += ball["speed_y"]

            # Отскок от стен
            if ball["x"] <= ball["radius"] or ball["x"] >= self.width - ball["radius"]:
                ball["speed_x"] = -ball["speed_x"]
            if ball["y"] <= ball["radius"]:
                ball["speed_y"] = -ball["speed_y"]

            # Проверка падения мяча (не удаляем сразу, только помечаем)
            if ball["y"] > self.height:
                continue  # Не удаляем мяч сразу, он будет удален когда упадут все мячи

            # Проверка столкновения дополнительного мяча с блоками
            ball_rect = pygame.Rect(
                ball["x"] - ball["radius"],
                ball["y"] - ball["radius"],
                ball["radius"] * 2,
                ball["radius"] * 2,
            )

            # Проверяем столкновения по отдельным осям для большей точности
            # Сначала проверяем движение по X
            if ball["speed_x"] != 0:
                future_x = ball["x"] + ball["speed_x"]
                ball_rect_x = pygame.Rect(
                    future_x - ball["radius"],
                    ball["y"] - ball["radius"],
                    ball["radius"] * 2,
                    ball["radius"] * 2,
                )

                for block in self.blocks:
                    if not block["destroyed"] and block["rect"].colliderect(ball_rect_x):
                        ball["speed_x"] = -ball["speed_x"]
                        block["destroyed"] = True
                        self.score += block["points"]

                        # Генерация ракеты с вероятностью 15%
                        if random.randint(1, 7) == 1:
                            rocket_x = block["rect"].centerx - self.rocket_width // 2
                            rocket_y = block["rect"].bottom
                            self.rockets.append({"x": rocket_x, "y": rocket_y, "flame_timer": 0.0})

                        # Генерация дополнительных мячей от дополнительных мячей с меньшей вероятностью (10%)
                        if random.randint(1, 10) == 1:
                            for j in range(3):
                                angle = (j * 120) + random.randint(
                                    -30, 30
                                )  # Разлет в разные стороны
                                speed_x = math.cos(math.radians(angle)) * self.target_ball_speed
                                speed_y = math.sin(math.radians(angle)) * self.target_ball_speed

                                self.extra_balls.append(
                                    {
                                        "x": block["rect"].centerx,
                                        "y": block["rect"].centery,
                                        "speed_x": speed_x,
                                        "speed_y": speed_y,
                                        "radius": self.ball_radius,
                                    }
                                )
                        break

            # Затем проверяем движение по Y
            if ball["speed_y"] != 0:
                future_y = ball["y"] + ball["speed_y"]
                ball_rect_y = pygame.Rect(
                    ball["x"] - ball["radius"],
                    future_y - ball["radius"],
                    ball["radius"] * 2,
                    ball["radius"] * 2,
                )

                for block in self.blocks:
                    if not block["destroyed"] and block["rect"].colliderect(ball_rect_y):
                        ball["speed_y"] = -ball["speed_y"]
                        block["destroyed"] = True
                        self.score += block["points"]

                        # Генерация ракеты с вероятностью 15%
                        if random.randint(1, 7) == 1:
                            rocket_x = block["rect"].centerx - self.rocket_width // 2
                            rocket_y = block["rect"].bottom
                            self.rockets.append({"x": rocket_x, "y": rocket_y, "flame_timer": 0.0})

                        # Генерация дополнительных мячей от дополнительных мячей с меньшей вероятностью (10%)
                        if random.randint(1, 10) == 1:
                            for j in range(3):
                                angle = (j * 120) + random.randint(
                                    -30, 30
                                )  # Разлет в разные стороны
                                speed_x = math.cos(math.radians(angle)) * self.target_ball_speed
                                speed_y = math.sin(math.radians(angle)) * self.target_ball_speed

                                self.extra_balls.append(
                                    {
                                        "x": block["rect"].centerx,
                                        "y": block["rect"].centery,
                                        "speed_x": speed_x,
                                        "speed_y": speed_y,
                                        "radius": self.ball_radius,
                                    }
                                )
                        break

            # Проверка столкновения с платформой
            ball_rect = pygame.Rect(
                ball["x"] - ball["radius"],
                ball["y"] - ball["radius"],
                ball["radius"] * 2,
                ball["radius"] * 2,
            )
            if paddle_rect.colliderect(ball_rect) and ball["speed_y"] > 0:
                # Угол отскока зависит от места попадания (максимум 100 градусов)
                hit_pos = (ball["x"] - self.paddle_x) / self.paddle_width
                bounce_angle: float = (hit_pos - 0.5) * 2  # От -1 до 1
                bounce_angle = max(
                    -0.87, min(0.87, bounce_angle)
                )  # Ограничиваем угол до ±100 градусов (sin(100°) ≈ 0.87)

                ball["speed_x"] = bounce_angle * self.target_ball_speed
                ball["speed_y"] = -abs(ball["speed_y"])

                # Корректировка позиции мяча
                ball["y"] = self.paddle_y - ball["radius"]

        # Удаление упавших дополнительных мячей происходит только когда упадут все мячи
        # (обрабатывается в логике проверки падения всех мячей)

        # Проверка падения основного мяча
        main_ball_fell = False
        if self.ball_y > self.height:
            main_ball_fell = True

        # Проверка падения всех дополнительных мячей
        all_extra_balls_fell = len(self.extra_balls) == 0 or all(
            ball["y"] > self.height for ball in self.extra_balls
        )

        # Жизнь отнимается только если упали ВСЕ мячи
        if main_ball_fell and all_extra_balls_fell:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
            else:
                # Перезапуск основного мяча
                self.ball_x = self.width // 2
                self.ball_y = self.paddle_y - self.ball_radius - 5
                self.ball_speed_x = random.choice([-5, 5])
                self.ball_speed_y = -5
                # Очистка всех дополнительных мячей
                self.extra_balls = []

        # Отскок от платформы
        ball_rect = pygame.Rect(
            self.ball_x - self.ball_radius,
            self.ball_y - self.ball_radius,
            self.ball_radius * 2,
            self.ball_radius * 2,
        )

        if paddle_rect.colliderect(ball_rect) and self.ball_speed_y > 0:
            # Синхронизация фактической скорости с установленной
            self.ball_speed = self.target_ball_speed

            # Угол отскока зависит от места попадания (максимум 100 градусов)
            hit_pos_paddle: float = (self.ball_x - self.paddle_x) / self.paddle_width
            angle_paddle: float = (hit_pos_paddle - 0.5) * 2  # От -1 до 1
            angle_paddle = max(
                -0.87, min(0.87, angle_paddle)
            )  # Ограничиваем угол до ±100 градусов (sin(100°) ≈ 0.87)

            self.ball_speed_x = angle_paddle * self.ball_speed
            self.ball_speed_y = -abs(self.ball_speed_y)

            # Корректировка позиции мяча
            self.ball_y = self.paddle_y - self.ball_radius

        # Проверка завершения уровня
        if all(block["destroyed"] for block in self.blocks):
            self.level_complete = True

    def check_block_collisions(self) -> None:
        """Проверка столкновений с блоками"""
        # Проверяем столкновения по отдельным осям для большей точности
        # Сначала проверяем движение по X
        if self.ball_speed_x != 0:
            future_x = self.ball_x + self.ball_speed_x
            ball_rect_x = pygame.Rect(
                future_x - self.ball_radius,
                self.ball_y - self.ball_radius,
                self.ball_radius * 2,
                self.ball_radius * 2,
            )

            for block in self.blocks:
                if not block["destroyed"] and block["rect"].colliderect(ball_rect_x):
                    self.ball_speed_x = -self.ball_speed_x
                    block["destroyed"] = True
                    self.score += block["points"]

                    # Генерация ракеты с вероятностью 15%
                    if random.randint(1, 7) == 1:
                        rocket_x = block["rect"].centerx - self.rocket_width // 2
                        rocket_y = block["rect"].bottom
                        self.rockets.append({"x": rocket_x, "y": rocket_y, "flame_timer": 0.0})

                    # Генерация 3 дополнительных мячей с вероятностью 5%
                    if random.randint(1, 20) == 1:
                        for i in range(3):
                            angle = (i * 120) + random.randint(-30, 30)  # Разлет в разные стороны
                            speed_x = math.cos(math.radians(angle)) * self.target_ball_speed
                            speed_y = math.sin(math.radians(angle)) * self.target_ball_speed

                            self.extra_balls.append(
                                {
                                    "x": block["rect"].centerx,
                                    "y": block["rect"].centery,
                                    "speed_x": speed_x,
                                    "speed_y": speed_y,
                                    "radius": self.ball_radius,
                                }
                            )

                    return

        # Затем проверяем движение по Y
        if self.ball_speed_y != 0:
            future_y = self.ball_y + self.ball_speed_y
            ball_rect_y = pygame.Rect(
                self.ball_x - self.ball_radius,
                future_y - self.ball_radius,
                self.ball_radius * 2,
                self.ball_radius * 2,
            )

            for block in self.blocks:
                if not block["destroyed"] and block["rect"].colliderect(ball_rect_y):
                    self.ball_speed_y = -self.ball_speed_y
                    block["destroyed"] = True
                    self.score += block["points"]

                    # Генерация ракеты с вероятностью 15%
                    if random.randint(1, 7) == 1:
                        rocket_x = block["rect"].centerx - self.rocket_width // 2
                        rocket_y = block["rect"].bottom
                        self.rockets.append({"x": rocket_x, "y": rocket_y, "flame_timer": 0.0})

                    # Генерация 3 дополнительных мячей с вероятностью 5%
                    if random.randint(1, 20) == 1:
                        for i in range(3):
                            angle = (i * 120) + random.randint(-30, 30)  # Разлет в разные стороны
                            speed_x = math.cos(math.radians(angle)) * self.target_ball_speed
                            speed_y = math.sin(math.radians(angle)) * self.target_ball_speed

                            self.extra_balls.append(
                                {
                                    "x": block["rect"].centerx,
                                    "y": block["rect"].centery,
                                    "speed_x": speed_x,
                                    "speed_y": speed_y,
                                    "radius": self.ball_radius,
                                }
                            )

                    return

    def next_level(self) -> None:
        """Переход на следующий уровень"""
        self.level_complete = False
        self.level += 1
        self.ball_speed = min(self.ball_speed + 0.5, self.max_ball_speed)  # Ограничение скорости
        self.target_ball_speed = min(
            self.target_ball_speed + 0.5, self.max_ball_speed
        )  # Увеличиваем установленную скорость
        self.create_blocks()

        # Очистка ракет и дополнительных мячей
        self.rockets = []
        self.extra_balls = []

        # Перезапуск мяча
        self.ball_x = self.width // 2
        self.ball_y = self.paddle_y - self.ball_radius - 5
        self.ball_speed_x = random.choice([-self.ball_speed, self.ball_speed])
        self.ball_speed_y = -self.ball_speed

    def draw(self) -> None:
        """Отрисовка игры"""
        self.screen.fill(self.bg_color)

        if not self.game_over:
            # Отрисовка блоков
            for block in self.blocks:
                if not block["destroyed"]:
                    pygame.draw.rect(self.screen, block["color"], block["rect"])
                    pygame.draw.rect(self.screen, (255, 255, 255), block["rect"], 2)

            # Отрисовка платформы
            paddle_rect = pygame.Rect(
                self.paddle_x, self.paddle_y, self.paddle_width, self.paddle_height
            )
            pygame.draw.rect(self.screen, self.paddle_color, paddle_rect)
            pygame.draw.rect(self.screen, (255, 255, 255), paddle_rect, 2)

            # Отрисовка мяча
            pygame.draw.circle(
                self.screen, self.ball_color, (int(self.ball_x), int(self.ball_y)), self.ball_radius
            )
            pygame.draw.circle(
                self.screen,
                (200, 200, 200),
                (int(self.ball_x), int(self.ball_y)),
                self.ball_radius,
                2,
            )

            # Отрисовка ракет
            for rocket in self.rockets:
                # Корпус ракеты
                rocket_rect = pygame.Rect(
                    rocket["x"], rocket["y"], self.rocket_width, self.rocket_height
                )
                pygame.draw.rect(self.screen, (150, 150, 150), rocket_rect)
                pygame.draw.rect(self.screen, (200, 200, 200), rocket_rect, 2)

                # Крылья ракеты (маленькие треугольники вверху)
                wing_size = 6
                left_wing = [
                    (rocket["x"] - wing_size, rocket["y"] + 8),
                    (rocket["x"], rocket["y"] + 4),
                    (rocket["x"], rocket["y"] + 12),
                ]
                right_wing = [
                    (rocket["x"] + self.rocket_width + wing_size, rocket["y"] + 8),
                    (rocket["x"] + self.rocket_width, rocket["y"] + 4),
                    (rocket["x"] + self.rocket_width, rocket["y"] + 12),
                ]
                pygame.draw.polygon(self.screen, (120, 120, 120), left_wing)
                pygame.draw.polygon(self.screen, (120, 120, 120), right_wing)

                # Заостренный нос ракеты (внизу) - правильный треугольник
                nose_points = [
                    (rocket["x"] + self.rocket_width // 2, rocket["y"] + self.rocket_height + 8),
                    (rocket["x"], rocket["y"] + self.rocket_height - 2),
                    (rocket["x"] + self.rocket_width - 1, rocket["y"] + self.rocket_height - 2),
                ]
                pygame.draw.polygon(self.screen, (180, 180, 180), nose_points)
                pygame.draw.polygon(self.screen, (200, 200, 200), nose_points, 1)

                # Пламя из сопла (анимированное, вверху)
                flame_intensity = int(5 + 3 * abs(math.sin(rocket["flame_timer"])))
                flame_colors = [(255, 100, 0), (255, 150, 0), (255, 200, 0)]

                for i in range(flame_intensity):
                    flame_y = rocket["y"] - i * 2
                    flame_width = max(2, self.rocket_width - i * 2)
                    flame_x = rocket["x"] + (self.rocket_width - flame_width) // 2

                    flame_color = flame_colors[min(i, len(flame_colors) - 1)]
                    pygame.draw.rect(self.screen, flame_color, (flame_x, flame_y, flame_width, 2))

            # Отрисовка дополнительных мячей
            for ball in self.extra_balls:
                pygame.draw.circle(
                    self.screen, self.ball_color, (int(ball["x"]), int(ball["y"])), ball["radius"]
                )
                pygame.draw.circle(
                    self.screen,
                    (200, 200, 200),
                    (int(ball["x"]), int(ball["y"])),
                    ball["radius"],
                    2,
                )

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

        # Жизни
        lives_text = f"Жизни: {self.lives}"
        lives_surface = self.font.render(lives_text, True, self.text_color)
        self.screen.blit(lives_surface, (10, 90))

        # Информация о ракетах
        if self.rockets:
            rocket_text = f"🚀 Ракет на поле: {len(self.rockets)}"
            rocket_surface = self.small_font.render(rocket_text, True, (255, 150, 0))
            self.screen.blit(rocket_surface, (10, 130))

            warning_text = "⚠️ Избегайте ракет!"
            warning_surface = self.small_font.render(warning_text, True, (255, 100, 100))
            self.screen.blit(warning_surface, (10, 150))

        # Состояние игры
        if self.game_over:
            game_over_text = "ИГРА ОКОНЧЕНА!"
            game_over_surface = self.font.render(game_over_text, True, (255, 100, 100))
            game_over_rect = game_over_surface.get_rect(
                center=(self.width // 2, self.height // 2 - 50)
            )
            self.screen.blit(game_over_surface, game_over_rect)

            restart_text = "Пробел - Перезапуск"
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

        elif self.level_complete:
            complete_text = "УРОВЕНЬ ПРОЙДЕН!"
            complete_surface = self.font.render(complete_text, True, (100, 255, 100))
            complete_rect = complete_surface.get_rect(
                center=(self.width // 2, self.height // 2 - 50)
            )
            self.screen.blit(complete_surface, complete_rect)

            next_text = "Пробел - Следующий уровень"
            next_surface = self.small_font.render(next_text, True, self.text_color)
            next_rect = next_surface.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(next_surface, next_rect)

        # Управление
        controls = ["← → - Движение", "Пробел - Пауза/Продолжить", "ESC - Выход"]
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
        return "arkanoid"
