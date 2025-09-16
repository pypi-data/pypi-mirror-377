from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pygame

from ..sound_manager import sound_manager


class BaseGame(ABC):
    """Базовый класс для всех игр"""

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.sound_manager = sound_manager

    @abstractmethod
    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Обработка событий игры"""
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        """Обновление логики игры"""
        pass

    @abstractmethod
    def draw(self) -> None:
        """Отрисовка игры"""
        pass

    @abstractmethod
    def is_game_over(self) -> bool:
        """Проверка окончания игры"""
        pass

    @abstractmethod
    def get_score(self) -> int:
        """Получение текущего счета"""
        pass

    @abstractmethod
    def get_game_name(self) -> str:
        """Получение названия игры"""
        pass
