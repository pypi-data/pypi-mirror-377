"""Чистые функции игровой логики для тестирования."""

from __future__ import annotations

import math
import random
from typing import Any

import pygame

# ============================================================================
# ТЕТРИС - Логика фигур и очистки линий
# ============================================================================


def rotate_tetris_piece(shape: list[list[str]], rotation: int) -> list[str]:
    """Поворот фигуры тетриса."""
    return shape[rotation % len(shape)]


def is_valid_tetris_position(
    shape: list[str], x: int, y: int, grid_width: int, grid_height: int, grid: list[list[int]]
) -> bool:
    """Проверка валидности позиции фигуры тетриса."""
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell == "#":
                new_x = x + j
                new_y = y + i

                # Проверка границ
                if new_x < 0 or new_x >= grid_width or new_y >= grid_height:
                    return False

                # Проверка столкновения с уже установленными блоками
                if new_y >= 0 and grid[new_y][new_x] != 0:
                    return False

    return True


def place_tetris_piece(
    shape: list[str], x: int, y: int, color: int, grid: list[list[int]]
) -> list[list[int]]:
    """Размещение фигуры на поле тетриса."""
    new_grid = [row[:] for row in grid]  # Создаем копию сетки
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell == "#":
                new_x = x + j
                new_y = y + i
                if new_y >= 0:
                    new_grid[new_y][new_x] = color
    return new_grid


def clear_tetris_lines(grid: list[list[int]]) -> tuple[list[list[int]], int]:
    """Очистка заполненных линий в тетрисе."""
    grid_width = len(grid[0])
    lines_to_clear = []

    for y in range(len(grid)):
        if all(grid[y][x] != 0 for x in range(grid_width)):
            lines_to_clear.append(y)

    # Удаление линий
    new_grid = [row[:] for row in grid]  # Создаем копию

    # Удаляем линии в обратном порядке, чтобы индексы не сдвигались
    for y in reversed(lines_to_clear):
        del new_grid[y]

    # Добавляем пустые линии сверху
    for _ in range(len(lines_to_clear)):
        new_grid.insert(0, [0 for _ in range(grid_width)])

    return new_grid, len(lines_to_clear)


def calculate_tetris_score(lines_cleared: int, level: int) -> int:
    """Расчет очков за очищенные линии в тетрисе."""
    if lines_cleared == 0:
        return 0
    return lines_cleared * 100 * level


# ============================================================================
# ЗМЕЙКА - Логика движения и столкновений
# ============================================================================


def move_snake(
    snake: list[tuple[int, int]],
    direction: tuple[int, int],
    grid_width: int,
    grid_height: int,
    grow: bool = False,
) -> tuple[list[tuple[int, int]], bool]:
    """Движение змейки с проверкой столкновений."""
    if not snake:
        return snake, True

    head_x, head_y = snake[0]
    new_head = (head_x + direction[0], head_y + direction[1])

    # Проверка столкновения со стенами
    if (
        new_head[0] < 0
        or new_head[0] >= grid_width
        or new_head[1] < 0
        or new_head[1] >= grid_height
    ):
        return snake, True

    # Проверка столкновения с собой
    if new_head in snake:
        return snake, True

    # Добавление новой головы
    new_snake = [new_head] + snake

    # Удаление хвоста если змейка не растет
    if not grow:
        new_snake.pop()

    return new_snake, False


def check_food_collision(snake: list[tuple[int, int]], food: tuple[int, int] | None) -> bool:
    """Проверка столкновения змейки с едой."""
    if not snake or food is None:
        return False
    return snake[0] == food


def generate_food_position(
    snake: list[tuple[int, int]],
    grid_width: int,
    grid_height: int,
    existing_items: list[tuple[int, int]] | None = None,
) -> tuple[int, int] | None:
    """Генерация позиции еды для змейки."""
    if existing_items is None:
        existing_items = []

    attempts = 0
    max_attempts = 1000  # Увеличиваем количество попыток

    while attempts < max_attempts:
        x = random.randint(0, grid_width - 1)
        y = random.randint(0, grid_height - 1)

        if (x, y) not in snake and (x, y) not in existing_items:
            return (x, y)
        attempts += 1

    return None


# ============================================================================
# АРКАНОИД - Логика столкновений мяча
# ============================================================================


def calculate_ball_reflection(
    ball_x: float,
    ball_y: float,
    ball_speed_x: float,
    ball_speed_y: float,
    ball_radius: int,
    paddle_x: float,
    paddle_y: float,
    paddle_width: int,
    paddle_height: int,
) -> tuple[float, float, float, float]:
    """Расчет отскока мяча от платформы."""
    ball_rect = pygame.Rect(
        ball_x - ball_radius,
        ball_y - ball_radius,
        ball_radius * 2,
        ball_radius * 2,
    )
    paddle_rect = pygame.Rect(paddle_x, paddle_y, paddle_width, paddle_height)

    if paddle_rect.colliderect(ball_rect) and ball_speed_y > 0:
        # Угол отскока зависит от места попадания
        hit_pos = (ball_x - paddle_x) / paddle_width
        angle = (hit_pos - 0.5) * 2  # От -1 до 1
        angle = max(-0.87, min(0.87, angle))  # Ограничиваем угол

        # Используем текущую скорость мяча
        current_speed = math.sqrt(ball_speed_x**2 + ball_speed_y**2)
        new_speed_x = angle * current_speed
        new_speed_y = -abs(ball_speed_y)

        # Корректировка позиции мяча
        new_ball_y = paddle_y - ball_radius

        return ball_x, new_ball_y, new_speed_x, new_speed_y

    return ball_x, ball_y, ball_speed_x, ball_speed_y


def check_block_collision(
    ball_x: float,
    ball_y: float,
    _ball_speed_x: float,
    _ball_speed_y: float,
    ball_radius: int,
    blocks: list[dict[str, Any]],
) -> tuple[bool, list[dict[str, Any]], int]:
    """Проверка столкновения мяча с блоками."""
    ball_rect = pygame.Rect(
        ball_x - ball_radius,
        ball_y - ball_radius,
        ball_radius * 2,
        ball_radius * 2,
    )

    new_blocks = blocks.copy()
    score_gained = 0

    for block in new_blocks:
        if not block["destroyed"] and block["rect"].colliderect(ball_rect):
            block["destroyed"] = True
            score_gained += block["points"]
            return True, new_blocks, score_gained

    return False, new_blocks, score_gained


# ============================================================================
# ПАКМАН - Логика движения и лабиринта
# ============================================================================


def is_valid_maze_position(
    x: int, y: int, maze: list[list[int]], maze_width: int, maze_height: int
) -> bool:
    """Проверка валидности позиции в лабиринте."""
    if x < 0 or x >= maze_width or y < 0 or y >= maze_height:
        return False
    return maze[y][x] != 1  # 1 = стена


def get_next_maze_position(x: int, y: int, direction: int) -> tuple[int, int]:
    """Получение следующей позиции в лабиринте по направлению."""
    directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # right, down, left, up
    dx, dy = directions[direction]
    return x + dx, y + dy


def check_dot_collision(pacman_x: int, pacman_y: int, maze: list[list[int]]) -> bool:
    """Проверка столкновения пакмана с точкой."""
    if pacman_x < 0 or pacman_x >= len(maze[0]) or pacman_y < 0 or pacman_y >= len(maze):
        return False
    return maze[pacman_y][pacman_x] == 2  # 2 = точка


def remove_dot_from_maze(pacman_x: int, pacman_y: int, maze: list[list[int]]) -> list[list[int]]:
    """Удаление точки из лабиринта."""
    new_maze = [row[:] for row in maze]  # Копируем лабиринт
    if pacman_x >= 0 and pacman_x < len(new_maze[0]) and pacman_y >= 0 and pacman_y < len(new_maze):
        new_maze[pacman_y][pacman_x] = 0  # 0 = пустое место
    return new_maze


def check_ghost_collision(
    pacman_x: int, pacman_y: int, ghosts: list[dict[str, Any]]
) -> tuple[bool, str]:
    """Проверка столкновения пакмана с призраком."""
    for ghost in ghosts:
        if ghost["x"] == pacman_x and ghost["y"] == pacman_y:
            return True, ghost["mode"]
    return False, ""


# ============================================================================
# ОБЩИЕ УТИЛИТЫ
# ============================================================================


def calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Расчет расстояния между двумя точками."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Ограничение значения в диапазоне."""
    return max(min_val, min(max_val, value))


def normalize_vector(x: float, y: float) -> tuple[float, float]:
    """Нормализация вектора."""
    length = math.sqrt(x**2 + y**2)
    if length == 0:
        return 0.0, 0.0
    return x / length, y / length
