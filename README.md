# Система учёта заявок в техподдержку (статусы, приоритеты, сроки)

## Установка и запуск

### С помощью uv

```bash
# Установка uv
pip install uv

# Установка зависимостей проекта
uv sync

# Применить миграции
uv run manage.py migrate

# Создать тестовые данные
uv run python manage.py init_data

# Запустить сервер
uv run manage.py runserver
```

Открыть в браузере: <http://127.0.0.1:8000>

### С помощью pip

```bash
# Создать виртуальное окружение
python -m venv venv

# Активировать виртуальное окружение
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

# Установка зависимостей проекта
pip install -r requirements.txt

# Применить миграции
python manage.py migrate

# Создать тестовые данные
python manage.py init_data

# Запустить сервер
python manage.py runserver
```

Открыть в браузере: <http://127.0.0.1:8000>
