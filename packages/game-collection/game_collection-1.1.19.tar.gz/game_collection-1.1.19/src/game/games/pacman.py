from __future__ import annotations

import math
import random
from typing import Any

import pygame

from .base import BaseGame


class PacmanGame(BaseGame):
    def __init__(self, screen: pygame.Surface) -> None:
        super().__init__(screen)
        self.width, self.height = screen.get_size()

        # Размеры лабиринта
        self.maze_width: int = 19
        self.maze_height: int = 21
        self.cell_size: int = min(self.width // self.maze_width, self.height // self.maze_height)

        # Позиция лабиринта на экране
        self.maze_x: int = (self.width - self.maze_width * self.cell_size) // 2
        self.maze_y: int = (self.height - self.maze_height * self.cell_size) // 2

        # Цвета
        self.bg_color: tuple[int, int, int] = (0, 0, 0)
        self.wall_color: tuple[int, int, int] = (0, 0, 255)
        self.dot_color: tuple[int, int, int] = (255, 255, 0)
        self.pacman_color: tuple[int, int, int] = (255, 255, 0)
        self.ghost_colors: list[tuple[int, int, int]] = [
            (255, 0, 0),
            (255, 0, 255),
            (0, 255, 255),
            (255, 165, 0),
        ]
        self.text_color: tuple[int, int, int] = (255, 255, 255)

        # Шрифты
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Лабиринт будет генерироваться программно
        self.maze: list[list[int]] = self.generate_maze()

        # Позиция Pac-Man
        self.pacman_x: int = 9
        self.pacman_y: int = 15
        self.pacman_direction: int = 0  # 0=вправо, 1=вниз, 2=влево, 3=вверх
        self.pacman_next_direction: int = 0
        self.pacman_moving: bool = False  # Движется ли Pac-Man
        self.eating_animation: float = 0.0  # Анимация поедания точки

        # Призраки
        self.ghosts: list[dict[str, Any]] = []
        ghost_positions = [(9, 9), (8, 9), (10, 9), (9, 10)]
        for i, (gx, gy) in enumerate(ghost_positions):
            self.ghosts.append(
                {
                    "x": gx,
                    "y": gy,
                    "direction": random.randint(0, 3),
                    "color": self.ghost_colors[i],
                    "mode": "chase",  # chase, scatter, frightened
                }
            )

        # Игровое состояние
        self.score: int = 0
        self.lives: int = 3
        self.game_over: bool = False
        self.paused: bool = False
        self.level: int = 1

        # Таймеры
        self.time: float = 0
        self.ghost_timer: float = 0
        self.power_pellet_timer: float = 0
        self.ghost_move_timer: float = 0
        self.pacman_move_timer: float = 0
        self.pacman_step_timer: float = 0

        # Анимация
        self.pacman_animation: float = 0
        self.ghost_animation: float = 0

    def reset_game(self) -> None:
        """Сброс игры"""
        # Генерируем новый лабиринт
        self.maze = self.generate_maze()

        # Позиция Pac-Man
        self.pacman_x = 9
        self.pacman_y = 15
        self.pacman_direction = 0
        self.pacman_next_direction = 0

        # Призраки
        ghost_positions = [(9, 9), (8, 9), (10, 9), (9, 10)]
        for i, ghost in enumerate(self.ghosts):
            ghost["x"] = ghost_positions[i][0]
            ghost["y"] = ghost_positions[i][1]
            ghost["direction"] = random.randint(0, 3)
            ghost["mode"] = "chase"

        # Состояние игры
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.paused = False
        self.level = 1
        self.time = 0
        self.ghost_timer = 0
        self.power_pellet_timer = 0

    def generate_maze(self) -> list[list[int]]:
        """Генерация случайного лабиринта с проверкой связности"""
        # Создаем базовую структуру лабиринта
        maze = [[1 for _ in range(self.maze_width)] for _ in range(self.maze_height)]

        # Создаем проходы с помощью простого алгоритма
        for y in range(1, self.maze_height - 1, 2):
            for x in range(1, self.maze_width - 1, 2):
                maze[y][x] = 2  # Точки в нечетных позициях

                # Создаем случайные проходы
                if (
                    random.random() < 0.7 and x + 1 < self.maze_width - 1
                ):  # 70% шанс горизонтального прохода
                    maze[y][x + 1] = 2

                if (
                    random.random() < 0.7 and y + 1 < self.maze_height - 1
                ):  # 70% шанс вертикального прохода
                    maze[y + 1][x] = 2

        # Добавляем дополнительные проходы для связности
        for _ in range(15):  # Увеличиваем количество дополнительных проходов
            x = random.randint(1, self.maze_width - 2)
            y = random.randint(1, self.maze_height - 2)
            if maze[y][x] == 1:  # Если это стена
                maze[y][x] = 2  # Делаем проходом

        # Убеждаемся, что есть проходы в центре для Pac-Man и призраков
        center_x, center_y = self.maze_width // 2, self.maze_height // 2
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                nx, ny = center_x + dx, center_y + dy
                if 0 <= nx < self.maze_width and 0 <= ny < self.maze_height:
                    maze[ny][nx] = 2

        # Убеждаемся, что стартовая позиция Pac-Man доступна
        start_x, start_y = 9, 15
        maze[start_y][start_x] = 2
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = start_x + dx, start_y + dy
            if 0 <= nx < self.maze_width and 0 <= ny < self.maze_height:
                maze[ny][nx] = 2

        # Проверяем связность и исправляем недоступные области
        maze = self._ensure_connectivity(maze)

        return maze

    def _ensure_connectivity(self, maze: list[list[int]]) -> list[list[int]]:
        """Обеспечивает связность лабиринта - все точки должны быть доступны"""
        # Находим все области с точками
        visited = [[False for _ in range(self.maze_width)] for _ in range(self.maze_height)]
        areas = []

        for y in range(self.maze_height):
            for x in range(self.maze_width):
                if maze[y][x] == 2 and not visited[y][x]:
                    # Находим область с точками
                    area = self._flood_fill(maze, x, y, visited)
                    if area:
                        areas.append(area)

        # Если есть только одна область - все хорошо
        if len(areas) <= 1:
            return maze

        # Если есть несколько областей - соединяем их
        print(f"Найдено {len(areas)} изолированных областей, соединяем...")

        # Соединяем первую область с остальными
        main_area = areas[0]
        for i in range(1, len(areas)):
            other_area = areas[i]
            # Находим ближайшие точки между областями
            min_dist = float("inf")
            best_path = None

            for x1, y1 in main_area:
                for x2, y2 in other_area:
                    dist = abs(x1 - x2) + abs(y1 - y2)
                    if dist < min_dist:
                        min_dist = dist
                        best_path = (x1, y1, x2, y2)

            if best_path:
                # Создаем путь между областями
                x1, y1, x2, y2 = best_path
                self._create_path(maze, x1, y1, x2, y2)
                # Добавляем точки из второй области в первую
                main_area.extend(other_area)

        return maze

    def _flood_fill(
        self, maze: list[list[int]], start_x: int, start_y: int, visited: list[list[bool]]
    ) -> list[tuple[int, int]]:
        """Находит все связанные точки в области"""
        if start_x < 0 or start_x >= self.maze_width or start_y < 0 or start_y >= self.maze_height:
            return []

        if visited[start_y][start_x] or maze[start_y][start_x] != 2:
            return []

        visited[start_y][start_x] = True
        area = [(start_x, start_y)]

        # Проверяем соседние клетки
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = start_x + dx, start_y + dy
            if (
                0 <= nx < self.maze_width
                and 0 <= ny < self.maze_height
                and not visited[ny][nx]
                and maze[ny][nx] == 2
            ):
                area.extend(self._flood_fill(maze, nx, ny, visited))

        return area

    def _create_path(self, maze: list[list[int]], x1: int, y1: int, x2: int, y2: int) -> None:
        """Создает путь между двумя точками"""
        # Простой алгоритм - сначала по горизонтали, потом по вертикали
        current_x, current_y = x1, y1

        # Движемся по горизонтали
        while current_x != x2:
            if current_x < x2:
                current_x += 1
            else:
                current_x -= 1
            maze[current_y][current_x] = 2

        # Движемся по вертикали
        while current_y != y2:
            if current_y < y2:
                current_y += 1
            else:
                current_y -= 1
            maze[current_y][current_x] = 2

    def next_level(self) -> None:
        """Переход на следующий уровень"""
        self.level += 1

        # Генерируем новый лабиринт
        self.maze = self.generate_maze()

        # Позиция Pac-Man
        self.pacman_x = 9
        self.pacman_y = 15
        self.pacman_direction = 0
        self.pacman_next_direction = 0
        self.pacman_moving = False

        # Призраки
        ghost_positions = [(9, 9), (8, 9), (10, 9), (9, 10)]
        for i, ghost in enumerate(self.ghosts):
            ghost["x"] = ghost_positions[i][0]
            ghost["y"] = ghost_positions[i][1]
            ghost["direction"] = random.randint(0, 3)
            ghost["mode"] = "chase"

        # Сброс таймеров
        self.ghost_move_timer = 0
        self.pacman_step_timer = 0

    def is_valid_position(self, x: int, y: int) -> bool:
        """Проверка валидности позиции"""
        if x < 0 or x >= self.maze_width or y < 0 or y >= self.maze_height:
            return False
        return self.maze[y][x] != 1

    def get_next_position(self, x: int, y: int, direction: int) -> tuple[int, int]:
        """Получение следующей позиции по направлению"""
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # вправо, вниз, влево, вверх
        dx, dy = directions[direction]
        return x + dx, y + dy

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Обработка событий"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pass  # ESC обрабатывается в main.py
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()
                elif event.key == pygame.K_RIGHT:
                    self.pacman_next_direction = 0
                    self.pacman_moving = True
                elif event.key == pygame.K_DOWN:
                    self.pacman_next_direction = 1
                    self.pacman_moving = True
                elif event.key == pygame.K_LEFT:
                    self.pacman_next_direction = 2
                    self.pacman_moving = True
                elif event.key == pygame.K_UP:
                    self.pacman_next_direction = 3
                    self.pacman_moving = True
            elif event.type == pygame.KEYUP and event.key in [
                pygame.K_RIGHT,
                pygame.K_DOWN,
                pygame.K_LEFT,
                pygame.K_UP,
            ]:
                # Останавливаем движение при отпускании клавиш
                self.pacman_moving = False

    def update(self, dt: float) -> None:
        """Обновление игры"""
        if self.game_over or self.paused:
            return

        self.time += dt

        # Обновление анимации
        if self.pacman_moving:
            self.pacman_animation += dt * 10
        self.ghost_animation += dt * 5

        # Обновление анимации поедания
        if self.eating_animation > 0:
            self.eating_animation -= dt * 4  # Анимация длится 0.25 секунды
            if self.eating_animation < 0:
                self.eating_animation = 0

        # Движение Pac-Man
        self.update_pacman(dt)

        # Движение призраков
        self.update_ghosts(dt)

        # Проверка столкновений
        self.check_collisions()

        # Проверка завершения уровня
        dots_remaining = sum(row.count(2) for row in self.maze)
        if dots_remaining == 0:
            self.next_level()

    def update_pacman(self, dt: float) -> None:
        """Обновление Pac-Man"""
        # Pac-Man двигается только когда нажата клавиша
        if self.pacman_moving:
            self.pacman_step_timer += dt

            # Движение с задержкой между шагами
            if self.pacman_step_timer >= 0.2:  # Шаг каждые 0.2 секунды
                self.pacman_step_timer = 0

                # Проверка возможности смены направления
                next_x, next_y = self.get_next_position(
                    self.pacman_x, self.pacman_y, self.pacman_next_direction
                )
                if self.is_valid_position(next_x, next_y):
                    self.pacman_direction = self.pacman_next_direction

                # Движение в текущем направлении
                next_x, next_y = self.get_next_position(
                    self.pacman_x, self.pacman_y, self.pacman_direction
                )
                if self.is_valid_position(next_x, next_y):
                    self.pacman_x = next_x
                    self.pacman_y = next_y

                    # Сбор точки
                    if self.maze[self.pacman_y][self.pacman_x] == 2:
                        self.maze[self.pacman_y][self.pacman_x] = 0
                        self.score += 10
                        # Запускаем анимацию поедания
                        self.eating_animation = 1.0

    def update_ghosts(self, dt: float) -> None:
        """Обновление призраков"""
        self.ghost_move_timer += dt

        # Призраки двигаются медленнее чем Pac-Man
        if self.ghost_move_timer >= 0.3:  # Движение каждые 0.3 секунды
            self.ghost_move_timer = 0

            for ghost in self.ghosts:
                # Простой ИИ призраков
                if random.random() < 0.1:  # 10% шанс смены направления
                    ghost["direction"] = random.randint(0, 3)

                # Движение
                next_x, next_y = self.get_next_position(
                    int(ghost["x"]), int(ghost["y"]), int(ghost["direction"])
                )
                if self.is_valid_position(next_x, next_y):
                    ghost["x"] = next_x
                    ghost["y"] = next_y
                else:
                    # Смена направления при столкновении со стеной
                    ghost["direction"] = random.randint(0, 3)

    def check_collisions(self) -> None:
        """Проверка столкновений"""
        for ghost in self.ghosts:
            if ghost["x"] == self.pacman_x and ghost["y"] == self.pacman_y:
                if ghost["mode"] == "frightened":
                    # Pac-Man съедает призрака
                    ghost["x"] = 9
                    ghost["y"] = 9
                    self.score += 200
                else:
                    # Pac-Man теряет жизнь
                    self.lives -= 1
                    if self.lives > 0:
                        # Если еще есть жизни, перезапускаем уровень
                        self.reset_level()
                    else:
                        # Если жизней не осталось, игра окончена
                        self.game_over = True
                    break

    def reset_level(self) -> None:
        """Перезапуск уровня после потери жизни"""
        # Сбрасываем позиции Pac-Man и призраков
        self.pacman_x = 9
        self.pacman_y = 15
        self.pacman_direction = 0
        self.pacman_next_direction = 0
        self.pacman_moving = False
        self.pacman_step_timer = 0

        # Сбрасываем позиции призраков
        for ghost in self.ghosts:
            ghost["x"] = 9
            ghost["y"] = 9
            ghost["direction"] = random.randint(0, 3)

        # Сбрасываем таймеры
        self.ghost_move_timer = 0
        self.pacman_animation = 0

    def draw(self) -> None:
        """Отрисовка игры"""
        self.screen.fill(self.bg_color)

        # Отрисовка лабиринта
        for y in range(self.maze_height):
            for x in range(self.maze_width):
                screen_x = self.maze_x + x * self.cell_size
                screen_y = self.maze_y + y * self.cell_size

                if self.maze[y][x] == 1:  # Стена
                    pygame.draw.rect(
                        self.screen,
                        self.wall_color,
                        (screen_x, screen_y, self.cell_size, self.cell_size),
                    )
                elif self.maze[y][x] == 2:  # Точка
                    center_x = screen_x + self.cell_size // 2
                    center_y = screen_y + self.cell_size // 2
                    # Рисуем точку с обводкой для лучшей видимости
                    pygame.draw.circle(self.screen, self.dot_color, (center_x, center_y), 3)
                    pygame.draw.circle(self.screen, (255, 255, 255), (center_x, center_y), 3, 1)

        # Отрисовка Pac-Man
        self.draw_pacman()

        # Отрисовка призраков
        self.draw_ghosts()

        # Отрисовка UI
        self.draw_ui()

    def draw_pacman(self) -> None:
        """Отрисовка Pac-Man"""
        screen_x = self.maze_x + self.pacman_x * self.cell_size
        screen_y = self.maze_y + self.pacman_y * self.cell_size
        center_x = screen_x + self.cell_size // 2
        center_y = screen_y + self.cell_size // 2
        radius = self.cell_size // 2 - 2

        # Анимация рта (открывается и закрывается)
        mouth_open = 0.05 if self.eating_animation > 0 else 0.05  # Рот всегда одинакового размера

        # Направления: 0=вправо, 1=вниз, 2=влево, 3=вверх
        directions = [0, 90, 180, 270]
        base_angle = directions[self.pacman_direction]

        # Углы рта (больший угол = более открытый рот)
        mouth_angle = 45 + mouth_open * 45  # От 45 до 90 градусов
        start_angle = base_angle - mouth_angle
        end_angle = base_angle + mouth_angle

        # Рисуем Pac-Man
        if self.eating_animation > 0:
            # При поедании - плавная анимация закрытия рта
            # Сначала рисуем полный круг
            pygame.draw.circle(self.screen, self.pacman_color, (center_x, center_y), radius)

            # Затем рисуем черный сектор для рта (размер зависит от анимации)
            # При eating_animation = 1.0 рот полностью закрыт (сектор очень маленький)
            # При eating_animation = 0.0 рот полностью открыт (сектор нормального размера)
            animation_factor = self.eating_animation  # От 1.0 до 0.0

            # Размер рта зависит от анимации
            animated_mouth_angle = mouth_angle * (
                1.0 - animation_factor * 0.8
            )  # От mouth_angle до 0.2 * mouth_angle

            animated_start_angle = base_angle - animated_mouth_angle
            animated_end_angle = base_angle + animated_mouth_angle

            points = [(center_x, center_y)]  # Центр

            # Добавляем точки по окружности для сектора рта
            num_points = 30
            for i in range(num_points + 1):
                angle = (
                    animated_start_angle
                    + (animated_end_angle - animated_start_angle) * i / num_points
                )
                x = center_x + radius * math.cos(math.radians(angle))
                y = center_y + radius * math.sin(math.radians(angle))
                points.append((int(x), int(y)))

            # Рисуем черный сектор (рот)
            if len(points) > 2:
                pygame.draw.polygon(self.screen, self.bg_color, points)
        else:
            # Обычный Pac-Man с ртом
            # Сначала рисуем полный круг
            pygame.draw.circle(self.screen, self.pacman_color, (center_x, center_y), radius)

            # Затем рисуем черный сектор для рта
            points = [(center_x, center_y)]  # Центр

            # Добавляем точки по окружности для сектора рта
            num_points = 30
            for i in range(num_points + 1):
                angle = start_angle + (end_angle - start_angle) * i / num_points
                x = center_x + radius * math.cos(math.radians(angle))
                y = center_y + radius * math.sin(math.radians(angle))
                points.append((int(x), int(y)))

            # Рисуем черный сектор (рот)
            if len(points) > 2:
                pygame.draw.polygon(self.screen, self.bg_color, points)

        # Добавляем глаз
        # Глаз позиционируется на краю круга в зависимости от направления движения
        eye_offset = radius * 0.6  # Смещение от центра (на краю круга)

        if self.pacman_direction == 0:  # Вправо - глаз в верхней части справа
            eye_x = center_x + eye_offset * 0.3
            eye_y = center_y - eye_offset * 0.8
        elif self.pacman_direction == 1:  # Вниз - глаз в правой части снизу
            eye_x = center_x + eye_offset * 0.8
            eye_y = center_y + eye_offset * 0.3
        elif self.pacman_direction == 2:  # Влево - глаз в верхней части слева
            eye_x = center_x - eye_offset * 0.3
            eye_y = center_y - eye_offset * 0.8
        else:  # Вверх - глаз в левой части сверху
            eye_x = center_x - eye_offset * 0.8
            eye_y = center_y - eye_offset * 0.3

        eye_radius = max(3, radius // 6)  # Размер глаза зависит от размера Pac-Man

        # Рисуем глаз всегда (кроме когда рот полностью закрыт)
        if self.eating_animation <= 0.9:  # Глаз виден когда рот не полностью закрыт
            # Рисуем белый фон для глаза
            pygame.draw.circle(
                self.screen, (255, 255, 255), (int(eye_x), int(eye_y)), eye_radius + 1
            )
            # Рисуем черный зрачок
            pygame.draw.circle(self.screen, (0, 0, 0), (int(eye_x), int(eye_y)), eye_radius)

    def draw_ghosts(self) -> None:
        """Отрисовка призраков"""
        for ghost in self.ghosts:
            screen_x = self.maze_x + ghost["x"] * self.cell_size
            screen_y = self.maze_y + ghost["y"] * self.cell_size
            center_x = screen_x + self.cell_size // 2
            center_y = screen_y + self.cell_size // 2
            ghost_width = self.cell_size - 4
            ghost_height = self.cell_size - 4

            # Рисуем тело призрака (форма как у настоящего призрака)
            # Верхняя часть - полукруг
            pygame.draw.circle(
                self.screen,
                ghost["color"],
                (center_x, center_y - ghost_height // 4),
                ghost_width // 2,
            )

            # Нижняя часть - прямоугольник с волнистым низом
            ghost_rect = pygame.Rect(
                center_x - ghost_width // 2,
                center_y - ghost_height // 4,
                ghost_width,
                ghost_height // 2,
            )
            pygame.draw.rect(self.screen, ghost["color"], ghost_rect)

            # Волнистый низ призрака
            wave_points = []
            wave_height = ghost_height // 8
            wave_width = ghost_width // 4

            for i in range(5):
                x = center_x - ghost_width // 2 + i * wave_width
                if i % 2 == 0:
                    y = center_y + ghost_height // 4
                else:
                    y = center_y + ghost_height // 4 + wave_height
                wave_points.append((x, y))

            # Добавляем последнюю точку
            wave_points.append((center_x + ghost_width // 2, center_y + ghost_height // 4))

            # Рисуем волнистый низ
            if len(wave_points) > 2:
                pygame.draw.polygon(self.screen, ghost["color"], wave_points)

            # Глаза призрака
            eye_size = ghost_width // 8
            eye_y = center_y - ghost_height // 6

            # Левый глаз
            pygame.draw.circle(
                self.screen, (255, 255, 255), (center_x - ghost_width // 4, eye_y), eye_size
            )
            pygame.draw.circle(
                self.screen, (0, 0, 0), (center_x - ghost_width // 4, eye_y), eye_size // 2
            )

            # Правый глаз
            pygame.draw.circle(
                self.screen, (255, 255, 255), (center_x + ghost_width // 4, eye_y), eye_size
            )
            pygame.draw.circle(
                self.screen, (0, 0, 0), (center_x + ghost_width // 4, eye_y), eye_size // 2
            )

    def is_game_over(self) -> bool:
        """Проверка окончания игры"""
        return self.game_over

    def get_score(self) -> int:
        """Получение счета"""
        return self.score

    def get_game_name(self) -> str:
        """Получение названия игры"""
        return "pacman"

    def draw_ui(self) -> None:
        """Отрисовка пользовательского интерфейса"""
        # Счет
        score_text = f"Счет: {self.score}"
        score_surface = self.font.render(score_text, True, self.text_color)
        self.screen.blit(score_surface, (10, 10))

        # Жизни
        lives_text = f"Жизни: {self.lives}"
        lives_surface = self.font.render(lives_text, True, self.text_color)
        self.screen.blit(lives_surface, (10, 50))

        # Уровень
        level_text = f"Уровень: {self.level}"
        level_surface = self.font.render(level_text, True, self.text_color)
        self.screen.blit(level_surface, (10, 90))

        # Управление
        controls = ["Стрелки - Движение", "SPACE - Пауза", "ESC - Меню", "R - Перезапуск"]
        for i, control in enumerate(controls):
            control_surface = self.small_font.render(control, True, (150, 150, 150))
            self.screen.blit(control_surface, (10, self.height - 100 + i * 20))

        # Состояние игры
        if self.game_over:
            game_over_text = "ИГРА ОКОНЧЕНА!"
            game_over_surface = self.font.render(game_over_text, True, (255, 100, 100))
            game_over_rect = game_over_surface.get_rect(
                center=(self.width // 2, self.height // 2 - 50)
            )
            self.screen.blit(game_over_surface, game_over_rect)

            restart_text = "Нажмите R для перезапуска"
            restart_surface = self.font.render(restart_text, True, self.text_color)
            restart_rect = restart_surface.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(restart_surface, restart_rect)

            esc_text = "ESC - Выход в меню"
            esc_surface = self.font.render(esc_text, True, self.text_color)
            esc_rect = esc_surface.get_rect(center=(self.width // 2, self.height // 2 + 30))
            self.screen.blit(esc_surface, esc_rect)

        elif self.paused:
            pause_text = "ПАУЗА"
            pause_surface = self.font.render(pause_text, True, self.text_color)
            pause_rect = pause_surface.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(pause_surface, pause_rect)

            space_text = "SPACE - Продолжить"
            space_surface = self.font.render(space_text, True, self.text_color)
            space_rect = space_surface.get_rect(center=(self.width // 2, self.height // 2 + 40))
            self.screen.blit(space_surface, space_rect)
