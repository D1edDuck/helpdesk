.PHONY: format lint all

# Проверка и исправление форматирования
format:
	uv run ruff format
	uv run ruff check --fix

# Проверка форматирования и типов
lint:
	uv run ruff check
	uv run mypy .

# Запуск format и lint одной командой
all: format lint