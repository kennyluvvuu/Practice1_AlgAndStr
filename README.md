# player

Минималистичный аудиоплеер с темной монохромной темой, реализованный на базе кольцевого двусвязного списка с архитектурой MVP.

## Стек

- **Python**: 3.12
- **GUI**: CustomTkinter
- **Аудио**: Pygame (`pygame.mixer`)
- **Пакетный менеджер**: uv / pip
- **Качество**: Pylint (10.00/10), Unittest

## Запуск

### Вариант 1: через uv (рекомендуется)

```bash
uv sync
uv run python main.py
```

### Вариант 2: через venv и pip

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Тестирование и линтинг

```bash
python -m unittest test_linked_list.py
pylint --rcfile=.pylintrc src/ main.py linked_list.py test_linked_list.py
```

## Архитектура

- **`src/models/`** — модели данных и кольцевой двусвязный список (`LinkedList`, `Composition`, `PlayList`).
- **`src/services/`** — системный аудиосервис и управление плейлистами (`PlayerService`).
- **`src/ui/`** — модульные компоненты интерфейса (панели, треклист с Drag-and-Drop, плеер).
