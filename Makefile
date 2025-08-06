.PHONY: install test lint format run build up down clean docker-build docker-up docker-down docker-logs

# Development commands
install:
	poetry install

test:
	poetry run pytest tests/

lint:
	poetry run flake8 app tests
	poetry run black --check app tests

format:
	poetry run black app tests

run:
	poetry run uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000

# Docker commands
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name "*.egg" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".coverage" -exec rm -r {} +
	find . -type d -name "htmlcov" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	find . -type d -name ".ruff_cache" -exec rm -r {} + 
	find . -type d -name ".hypothesis" -exec rm -r {} + 