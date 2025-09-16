from __future__ import annotations

import random
from typing import Any

import pygame

from games.base import BaseGame


class TetrisGame(BaseGame):
    def __init__(self, screen: pygame.Surface) -> None:
        super().__init__(screen)
        self.width, self.height = screen.get_size()

        # Игровое поле
        self.grid_width = 10
        self.grid_height = 20
        self.cell_size = 30

        # Позиция игрового поля
        self.grid_x = (self.width - self.grid_width * self.cell_size) // 2
        self.grid_y = 50

        # Цвета
        self.bg_color = (20, 25, 40)
        self.grid_color = (50, 50, 70)
        self.text_color = (255, 255, 255)

        # Цвета фигур
        self.colors = [
            (0, 0, 0),  # Пустая клетка
            (255, 100, 100),  # I
            (100, 255, 100),  # O
            (100, 100, 255),  # T
            (255, 255, 100),  # S
            (255, 100, 255),  # Z
            (100, 255, 255),  # J
            (255, 200, 100),  # L
        ]

        # Шрифты
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Фигуры тетриса
        self.shapes = [
            # I
            [
                [".....", "..#..", "..#..", "..#..", "..#.."],
                [".....", ".....", "####.", ".....", "....."],
            ],
            # O
            [[".....", ".....", ".##..", ".##..", "....."]],
            # T
            [
                [".....", ".....", ".#...", "###..", "....."],
                [".....", ".....", ".#...", ".##..", ".#..."],
                [".....", ".....", ".....", "###..", ".#..."],
                [".....", ".....", ".#...", "##...", ".#..."],
            ],
            # S
            [
                [".....", ".....", ".##..", "##...", "....."],
                [".....", ".#...", ".##..", "..#..", "....."],
            ],
            # Z
            [
                [".....", ".....", "##...", ".##..", "....."],
                [".....", "..#..", ".##..", ".#...", "....."],
            ],
            # J
            [
                [".....", ".#...", ".#...", "##...", "....."],
                [".....", ".....", "#....", "###..", "....."],
                [".....", ".##..", ".#...", ".#...", "....."],
                [".....", ".....", "###..", "..#..", "....."],
            ],
            # L
            [
                [".....", ".#...", ".#...", ".##..", "....."],
                [".....", ".....", "###..", "#....", "....."],
                [".....", "##...", ".#...", ".#...", "....."],
                [".....", ".....", "..#..", "###..", "....."],
            ],
        ]

        # Инициализация игры
        self.reset_game()

        # Состояние игры
        self.game_over: bool = False
        self.paused: bool = False

    def reset_game(self) -> None:
        """Сброс игры"""
        # Игровое поле
        self.grid = [[0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]

        # Текущая фигура
        self.current_piece = self.get_new_piece()
        self.next_piece = self.get_new_piece()

        # Позиция фигуры
        self.piece_x: int = self.grid_width // 2 - 2
        self.piece_y: int = -1  # Фигура появляется на клетку выше

        # Счет и уровень
        self.score = 0
        self.level = 1
        self.lines_cleared = 0

        # Скорость падения
        self.fall_time: float = 0
        self.fall_speed: float = 0.5
        self.fast_fall_speed: float = 0.05  # Быстрое падение при зажатии вниз

        # Таймер для движения влево/вправо
        self.move_timer: float = 0

        # Состояние игры
        self.game_over = False
        self.paused = False

    def get_new_piece(self) -> dict[str, Any]:
        """Получение новой фигуры"""
        shape_index = random.randint(1, len(self.shapes))
        shape = self.shapes[shape_index - 1]
        return {"shape": shape, "rotation": 0, "color": shape_index}

    def get_rotated_shape(self, piece: dict[str, Any]) -> list[str]:
        """Получение повернутой фигуры"""
        shape: list[list[str]] = piece["shape"]
        rotation: int = piece["rotation"]
        return shape[rotation % len(shape)]

    def is_valid_position(self, piece: dict[str, Any], x: int, y: int) -> bool:
        """Проверка валидности позиции фигуры"""
        shape = self.get_rotated_shape(piece)

        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell == "#":
                    new_x = x + j
                    new_y = y + i

                    # Проверка границ
                    if new_x < 0 or new_x >= self.grid_width or new_y >= self.grid_height:
                        return False

                    # Проверка столкновения с уже установленными блоками
                    if new_y >= 0 and self.grid[new_y][new_x] != 0:
                        return False

        return True

    def place_piece(self, piece: dict[str, Any], x: int, y: int) -> None:
        """Размещение фигуры на поле"""
        shape = self.get_rotated_shape(piece)

        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell == "#":
                    new_x = x + j
                    new_y = y + i
                    if new_y >= 0:
                        self.grid[new_y][new_x] = piece["color"]

    def clear_lines(self) -> None:
        """Очистка заполненных линий"""
        lines_to_clear = []

        for y in range(self.grid_height):
            if all(self.grid[y][x] != 0 for x in range(self.grid_width)):
                lines_to_clear.append(y)

        # Удаление линий
        for y in lines_to_clear:
            del self.grid[y]
            self.grid.insert(0, [0 for _ in range(self.grid_width)])

        # Обновление счета
        if lines_to_clear:
            self.lines_cleared += len(lines_to_clear)
            self.score += len(lines_to_clear) * 100 * self.level

            # Проверка повышения уровня
            # Уровень 1: 7 линий, Уровень 2: 8 линий, Уровень 3: 9 линий, и т.д.
            required_lines = 7 + (self.level - 1)  # 7, 8, 9, 10, 11...
            if self.lines_cleared >= required_lines:
                self.level += 1
                self.lines_cleared = 0
                self.fall_speed = max(0.1, 0.5 - (self.level - 1) * 0.05)

    def handle_events(self, events: list[pygame.event.Event] | None = None) -> None:
        """Обработка событий"""
        if events is None:
            events = pygame.event.get()

        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.reset_game()
                elif self.paused:
                    if event.key == pygame.K_p:
                        self.paused = False
                else:
                    if event.key == pygame.K_DOWN:
                        if self.is_valid_position(
                            self.current_piece, self.piece_x, self.piece_y + 1
                        ):
                            self.piece_y += 1
                    elif event.key == pygame.K_UP:
                        # Поворот фигуры
                        new_piece = self.current_piece.copy()
                        new_piece["rotation"] = (new_piece["rotation"] + 1) % len(
                            new_piece["shape"]
                        )
                        if self.is_valid_position(new_piece, self.piece_x, self.piece_y):
                            self.current_piece = new_piece
                    elif event.key == pygame.K_SPACE:
                        # Быстрое падение
                        while self.is_valid_position(
                            self.current_piece, self.piece_x, self.piece_y + 1
                        ):
                            self.piece_y += 1
                    elif event.key == pygame.K_p:
                        self.paused = True

    def update(self, dt: float) -> None:
        """Обновление игры"""
        if self.game_over or self.paused:
            return

        # Проверка зажатия клавиш
        keys = pygame.key.get_pressed()
        fast_fall = keys[pygame.K_DOWN]
        fast_left = keys[pygame.K_LEFT]
        fast_right = keys[pygame.K_RIGHT]

        # Выбор скорости падения
        current_fall_speed = self.fast_fall_speed if fast_fall else self.fall_speed

        # Быстрое движение влево/вправо
        self.move_timer += dt
        move_speed = 0.1 if (fast_left or fast_right) else 0.2

        if self.move_timer >= move_speed:
            self.move_timer = 0

            if fast_left and self.is_valid_position(
                self.current_piece, self.piece_x - 1, self.piece_y
            ):
                self.piece_x -= 1
            elif fast_right and self.is_valid_position(
                self.current_piece, self.piece_x + 1, self.piece_y
            ):
                self.piece_x += 1

        # Падение фигуры
        self.fall_time += dt
        if self.fall_time >= current_fall_speed:
            self.fall_time = 0

            if self.is_valid_position(self.current_piece, self.piece_x, self.piece_y + 1):
                self.piece_y += 1
            else:
                # Фигура достигла дна или столкнулась
                self.place_piece(self.current_piece, self.piece_x, self.piece_y)
                self.clear_lines()

                # Новая фигура
                self.current_piece = self.next_piece
                self.next_piece = self.get_new_piece()
                self.piece_x = self.grid_width // 2 - 2
                self.piece_y = -1  # Фигура появляется на клетку выше

                # Проверка окончания игры
                if not self.is_valid_position(self.current_piece, self.piece_x, self.piece_y):
                    self.game_over = True

    def draw(self) -> None:
        """Отрисовка игры"""
        self.screen.fill(self.bg_color)

        # Отрисовка игрового поля
        self.draw_grid()

        # Отрисовка текущей фигуры
        if not self.game_over:
            self.draw_piece(self.current_piece, self.piece_x, self.piece_y)

        # Отрисовка следующей фигуры
        self.draw_next_piece()

        # Отрисовка интерфейса
        self.draw_ui()

    def draw_grid(self) -> None:
        """Отрисовка игрового поля"""
        # Фон поля
        grid_rect = pygame.Rect(
            self.grid_x,
            self.grid_y,
            self.grid_width * self.cell_size,
            self.grid_height * self.cell_size,
        )
        pygame.draw.rect(self.screen, self.grid_color, grid_rect)
        pygame.draw.rect(self.screen, (100, 100, 120), grid_rect, 2)

        # Клетки поля
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.grid[y][x] != 0:
                    cell_rect = pygame.Rect(
                        self.grid_x + x * self.cell_size,
                        self.grid_y + y * self.cell_size,
                        self.cell_size,
                        self.cell_size,
                    )
                    pygame.draw.rect(self.screen, self.colors[self.grid[y][x]], cell_rect)
                    pygame.draw.rect(self.screen, (255, 255, 255), cell_rect, 1)

    def draw_piece(self, piece: dict[str, Any], x: int, y: int) -> None:
        """Отрисовка фигуры"""
        shape = self.get_rotated_shape(piece)

        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell == "#":
                    cell_x = self.grid_x + (x + j) * self.cell_size
                    cell_y = self.grid_y + (y + i) * self.cell_size

                    if cell_y >= self.grid_y:  # Только видимые клетки
                        cell_rect = pygame.Rect(cell_x, cell_y, self.cell_size, self.cell_size)
                        pygame.draw.rect(self.screen, self.colors[piece["color"]], cell_rect)
                        pygame.draw.rect(self.screen, (255, 255, 255), cell_rect, 1)

    def draw_next_piece(self) -> None:
        """Отрисовка следующей фигуры"""
        next_x = self.grid_x + self.grid_width * self.cell_size + 20
        next_y = self.grid_y + 50

        # Заголовок
        next_text = "Следующая:"
        next_surface = self.small_font.render(next_text, True, self.text_color)
        self.screen.blit(next_surface, (next_x, next_y))

        # Фигура
        shape = self.get_rotated_shape(self.next_piece)
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell == "#":
                    cell_x = next_x + j * 20
                    cell_y = next_y + 30 + i * 20
                    cell_rect = pygame.Rect(cell_x, cell_y, 20, 20)
                    pygame.draw.rect(self.screen, self.colors[self.next_piece["color"]], cell_rect)
                    pygame.draw.rect(self.screen, (255, 255, 255), cell_rect, 1)

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

        # Прогресс до следующего уровня
        required_lines = 7 + self.level  # Следующий уровень требует 7 + текущий_уровень линий
        lines_needed = max(0, required_lines - self.lines_cleared)
        progress_text = f"До уровня {self.level + 1}: {lines_needed}"
        progress_surface = self.small_font.render(progress_text, True, self.text_color)
        self.screen.blit(progress_surface, (10, 90))

        # Состояние игры
        if self.game_over:
            game_over_text = "ИГРА ОКОНЧЕНА!"
            game_over_surface = self.font.render(game_over_text, True, (255, 100, 100))
            game_over_rect = game_over_surface.get_rect(
                center=(self.width // 2, self.height // 2 - 50)
            )
            self.screen.blit(game_over_surface, game_over_rect)

            restart_text = "R - Перезапуск"
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

            space_text = "P - Продолжить"
            space_surface = self.small_font.render(space_text, True, self.text_color)
            space_rect = space_surface.get_rect(center=(self.width // 2, self.height // 2 + 40))
            self.screen.blit(space_surface, space_rect)

        # Управление
        controls = [
            "Стрелки - Движение",
            "Вниз    - Быстрое падение",
            "Вверх   - Поворот",
            "Пробел  - Мгновенное падение",
            "P       - Пауза",
            "ESC     - Выход",
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
        return "tetris"
