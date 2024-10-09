SOURCES := $(shell find . -name '*.py')

.DEFAULT_GOAL := help
.PY = poetry run

DOCKER_COMPOSE_LOCAL_FILE = infra/docker-compose.yml

ENV_DEV_FILE = ./.env.local

define export_env
  export $(shell sed 's/=.*//' $(ENV_TEST_FILE))
endef

run: ## Run the project
	$(if $(findstring arm64,$(shell uname -m)),\
	DB_NAME=$(DB_NAME) DB_USER=$(DB_USER) DB_PASS=$(DB_PASS) DB_HOST=$(DB_HOST) DOCKER_DEFAULT_PLATFORM=linux/arm64 docker compose -f ${DOCKER_COMPOSE_LOCAL_FILE} up -d --build --no-deps --remove-orphans --force-recreate,\
	DB_NAME=$(DB_NAME) DB_USER=$(DB_USER) DB_PASS=$(DB_PASS) DB_HOST=$(DB_HOST) docker compose -f ${DOCKER_COMPOSE_LOCAL_FILE} up -d --build --no-deps --remove-orphans --force-recreate)
.PHONY: run

restart: ## Restart the project
	$(if $(findstring arm64,$(shell uname -m)),\
	DB_NAME=$(DB_NAME) DB_USER=$(DB_USER) DB_PASS=$(DB_PASS) DB_HOST=$(DB_HOST) DOCKER_DEFAULT_PLATFORM=linux/arm64 docker compose -f ${DOCKER_COMPOSE_LOCAL_FILE} restart,\
	DB_NAME=$(DB_NAME) DB_USER=$(DB_USER) DB_PASS=$(DB_PASS) DB_HOST=$(DB_HOST) docker compose -f ${DOCKER_COMPOSE_LOCAL_FILE} restart)
.PHONY: restart


down: ## Down the project
	$(if $(findstring arm64,$(shell uname -m)),\
	DB_NAME=$(DB_NAME) DB_USER=$(DB_USER) DB_PASS=$(DB_PASS) DB_HOST=$(DB_HOST) DOCKER_DEFAULT_PLATFORM=linux/arm64 docker compose -f ${DOCKER_COMPOSE_LOCAL_FILE} down,\
	DB_NAME=$(DB_NAME) DB_USER=$(DB_USER) DB_PASS=$(DB_PASS) DB_HOST=$(DB_HOST) docker compose -f ${DOCKER_COMPOSE_LOCAL_FILE} down)
.PHONY: down

help: ## Display this help screen
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
.PHONY: help

install: ## Install project dependencies
	poetry install --with dev --no-interaction --no-ansi --no-root
.PHONY: install

lint: ## Lint the source code
	$(.PY) ruff check --config pyproject.toml --no-fix $(SOURCES)
.PHONY: lint

format: ## Format the source code
	$(.PY) ruff check --config pyproject.toml --fix $(SOURCES)
	$(.PY) ruff format --config pyproject.toml $(SOURCES)
.PHONY: format

test: ## Run tests
	$(if $(findstring arm64,$(shell uname -m)),\
	DB_NAME=$(DB_NAME) DB_USER=$(DB_USER) DB_PASS=$(DB_PASS) DB_HOST=$(DB_HOST) DOCKER_DEFAULT_PLATFORM=linux/arm64 docker compose -f ${DOCKER_COMPOSE_LOCAL_FILE} run --rm web python onhires_drf_test_task/manage.py test wallet,\
	DB_NAME=$(DB_NAME) DB_USER=$(DB_USER) DB_PASS=$(DB_PASS) DB_HOST=$(DB_HOST) docker compose -f ${DOCKER_COMPOSE_LOCAL_FILE} run --rm web python onhires_drf_test_task/manage.py test wallet)
.PHONY: test