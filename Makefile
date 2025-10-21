.PHONY: build up down test run-linters

# Сборка проекта
build:
	docker compose --env-file local.env -f docker-compose-local.yml build

# Запуск сервиса
up:  build
	docker compose --env-file local.env -f docker-compose-local.yml up

# Остановка сервиса
down:
	docker compose --env-file local.env -f docker-compose-local.yml down

# Запуск линтеров
run-linters:
	flake8 .
	black --check --diff .
	mypy .
	isort --check-only --diff .

# Запуск тестов внутри контейнера weblite_framework
test:
	docker exec weblite_framework sh -lc "pytest tests -s -v"

# Сборка пакета
build-package:
	poetry build

# Публикация пакета
publish-package: build-package
	python -m twine upload dist/*
