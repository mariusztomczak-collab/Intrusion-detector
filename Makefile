.PHONY: install test lint format run build up down clean

install:
	poetry install

test:
	poetry run pytest tests/

lint:
	poetry run flake8 src/ tests/
	poetry run mypy src/ tests/
	poetry run black --check src/ tests/
	poetry run isort --check-only src/ tests/

format:
	poetry run black src/ tests/
	poetry run isort src/ tests/

run:
	poetry run uvicorn src.api.main:app --reload

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name "*.egg" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	find . -type d -name ".ruff_cache" -exec rm -r {} + 