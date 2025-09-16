from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import appdirs


class ScoreManager:
    def __init__(self) -> None:
        self.scores_file = self._get_scores_path()
        self.scores: dict[str, list[dict[str, Any]]] = self.load_scores()

    def _get_scores_path(self) -> Path:
        """Get the path to the scores file using appdirs."""
        # Use appdirs to get the appropriate data directory
        data_dir = Path(appdirs.user_data_dir("GameCollection", "hleserg"))
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir / "scores.json"

    def load_scores(self) -> dict[str, list[dict[str, Any]]]:
        """Загрузка рекордов из файла"""
        if self.scores_file.exists():
            try:
                with open(self.scores_file, encoding="utf-8") as f:
                    scores: dict[str, list[dict[str, Any]]] = json.load(f)
                    return scores
            except (OSError, json.JSONDecodeError):
                return {}
        return {}

    def save_scores(self) -> None:
        """Сохранение рекордов в файл"""
        try:
            with open(self.scores_file, "w", encoding="utf-8") as f:
                json.dump(self.scores, f, ensure_ascii=False, indent=2)
        except OSError:
            pass  # Игнорируем ошибки записи

    def add_score(self, game_name: str, score: int) -> None:
        """Добавление нового рекорда"""
        if game_name not in self.scores:
            self.scores[game_name] = []

        # Создаем запись о рекорде
        score_entry = {
            "player": "Игрок",  # Можно расширить для ввода имени
            "score": score,
            "date": datetime.now().strftime("%d.%m.%Y %H:%M"),
        }

        # Добавляем рекорд
        self.scores[game_name].append(score_entry)

        # Сортируем по убыванию очков
        self.scores[game_name].sort(key=lambda x: x["score"], reverse=True)

        # Оставляем только топ 10
        self.scores[game_name] = self.scores[game_name][:10]

        # Сохраняем
        self.save_scores()

    def get_scores(self, game_name: str) -> list[dict[str, Any]]:
        """Получение рекордов для конкретной игры"""
        return self.scores.get(game_name, [])

    def get_best_score(self, game_name: str) -> int:
        """Получение лучшего рекорда для игры"""
        scores = self.get_scores(game_name)
        if scores:
            score: int = scores[0]["score"]
            return score
        return 0

    def clear_scores(self, game_name: str | None = None) -> None:
        """Очистка рекордов"""
        if game_name:
            if game_name in self.scores:
                del self.scores[game_name]
        else:
            self.scores = {}
        self.save_scores()
