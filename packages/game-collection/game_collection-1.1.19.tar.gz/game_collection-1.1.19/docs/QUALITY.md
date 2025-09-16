# Качество кода

## Обзор

Проект использует современные инструменты для обеспечения высокого качества кода:

- **Ruff** - быстрый линтер и форматтер (заменяет flake8, isort, pyupgrade)
- **mypy** - статическая проверка типов
- **GitHub Actions** - автоматические проверки в CI/CD

## Инструменты

### Ruff

Ruff - это быстрый линтер и форматтер для Python, написанный на Rust. Он заменяет несколько инструментов:

- flake8 (pycodestyle, pyflakes)
- isort (сортировка импортов)
- pyupgrade (обновление синтаксиса)
- и многие другие

#### Настройка

Конфигурация находится в `pyproject.toml`:

```toml
[tool.ruff]
target-version = "py311"
line-length = 100

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
    "ARG", # flake8-unused-arguments
    "SIM", # flake8-simplify
    "TCH", # flake8-type-checking
]
```

#### Команды

```bash
# Проверка кода
make lint
# или
python -m ruff check games/ ui/ main.py

# Форматирование
python -m ruff format games/ ui/ main.py

# Автоисправление ошибок
python -m ruff check games/ ui/ main.py --fix
```

### mypy

mypy проверяет типы в Python коде и помогает находить ошибки до выполнения программы.

#### Настройка

Конфигурация в `pyproject.toml`:

```toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true
```

#### Команды

```bash
# Проверка типов
make typecheck
# или
python -m mypy games/ ui/ main.py --ignore-missing-imports
```

### Типизация

Весь код проекта полностью типизирован:

```python
from __future__ import annotations

def handle_events(self, events: list[pygame.event.Event]) -> None:
    """Обработка событий игры"""
    pass

def get_score(self) -> int:
    """Получение текущего счета"""
    return self.score

def update(self, dt: float) -> None:
    """Обновление логики игры"""
    pass
```

## Автоматизация

### Скрипт проверки качества

Файл `scripts/lint.py` запускает все проверки:

```bash
python scripts/lint.py
```

Этот скрипт:
1. Проверяет код с Ruff
2. Проверяет форматирование
3. Проверяет типы с mypy
4. Выводит сводный отчет

### Makefile команды

```bash
# Полная проверка качества
make quality

# Отдельные проверки
make lint       # Ruff линтер
make typecheck  # mypy
make format     # форматирование

# Все проверки
make check
```

### GitHub Actions

CI автоматически запускается при:
- Push в ветки main/develop
- Pull request в main

Проверяет код на Python 3.11 и 3.12.

## Преимущества

### Обнаружение ошибок

Типизация помогает находить ошибки в логике игр:

```python
# Ошибка будет найдена mypy
def collision_check(player: Player, enemy: Enemy) -> bool:
    return player.x == enemy.position  # Ошибка: разные типы координат
```

### Улучшение производительности

- Ruff работает в 10-100x быстрее чем flake8
- mypy помогает оптимизировать код

### Удобство разработки

- Автодополнение в IDE
- Документирование API через типы
- Легче рефакторинг

## Примеры типичных ошибок

### 1. Неправильные типы

```python
# Плохо
def move_player(speed):
    pass

# Хорошо
def move_player(speed: float) -> None:
    pass
```

### 2. Отсутствующие аннотации

```python
# Плохо
def get_high_score(game_name):
    return scores.get(game_name, 0)

# Хорошо
def get_high_score(self, game_name: str) -> int:
    scores = self.get_scores(game_name)
    if scores:
        return scores[0]["score"]
    return 0
```

### 3. Неиспользуемые переменные

```python
# Плохо
for i, item in enumerate(items):
    print(f"Item: {item}")  # i не используется

# Хорошо
for _i, item in enumerate(items):
    print(f"Item: {item}")
```

## Интеграция в разработку

1. **Перед коммитом** - запустите `make quality`
2. **В IDE** - настройте автоформатирование с Ruff
3. **При review** - CI автоматически проверит код
4. **При рефакторинге** - mypy поможет не сломать API

Это обеспечивает стабильность и качество кода в проекте игр!
