# mcmqtt Docker Compose Management

.PHONY: help dev prod build up down logs restart clean test shell broker-logs

# Default environment
ENV ?= dev

help: ## Show this help message
	@echo "mcmqtt Docker Compose Management"
	@echo "================================"
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ { printf "  %-15s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

dev: ## Start development environment with hot-reload
	@echo "Starting development environment..."
	@ENVIRONMENT=dev docker compose up --build -d
	@echo "Development server available at: http://mcmqtt.localhost"
	@$(MAKE) logs

prod: ## Start production environment
	@echo "Starting production environment..."
	@ENVIRONMENT=prod docker compose up --build -d
	@$(MAKE) logs

build: ## Build Docker images
	@echo "Building Docker images..."
	@docker compose build

up: ## Start services (respects ENVIRONMENT variable)
	@echo "Starting services in $(ENV) mode..."
	@ENVIRONMENT=$(ENV) docker compose up -d

down: ## Stop and remove all services
	@echo "Stopping all services..."
	@docker compose down

logs: ## Show logs from all services
	@echo "Showing logs (Ctrl+C to exit)..."
	@docker compose logs -f

broker-logs: ## Show MQTT broker logs specifically
	@echo "Showing MQTT broker logs (Ctrl+C to exit)..."
	@docker compose logs -f mqtt-broker

restart: ## Restart all services
	@echo "Restarting services..."
	@docker compose restart

clean: ## Stop services and remove volumes
	@echo "Cleaning up containers, networks, and volumes..."
	@docker compose down -v --remove-orphans
	@docker system prune -f

test: ## Run tests in container
	@echo "Running tests..."
	@docker compose exec mcmqtt-server uv run pytest

shell: ## Open shell in mcmqtt container
	@echo "Opening shell in mcmqtt container..."
	@docker compose exec mcmqtt-server /bin/bash

install: ## Install dependencies locally with uv
	@echo "Installing dependencies with uv..."
	@uv sync --dev

check: ## Run code quality checks
	@echo "Running code quality checks..."
	@uv run black --check src tests
	@uv run ruff check src tests
	@uv run mypy src

format: ## Format code with black and ruff
	@echo "Formatting code..."
	@uv run black src tests
	@uv run ruff check --fix src tests

status: ## Show status of all services
	@echo "Service Status:"
	@echo "==============="
	@docker compose ps

health: ## Check health of services
	@echo "Health Check:"
	@echo "============="
	@curl -f http://localhost:3000/health 2>/dev/null && echo "✅ mcmqtt-server: healthy" || echo "❌ mcmqtt-server: unhealthy"
	@mosquitto_pub -h localhost -t health -m 'test' 2>/dev/null && echo "✅ mqtt-broker: healthy" || echo "❌ mqtt-broker: unhealthy"