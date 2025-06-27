# Makefile for Medical Record Translator Docker operations

.PHONY: help build build-prod up down logs clean test shell-backend shell-frontend push

# Default target
help:
	@echo "Available commands:"
	@echo "  make build          - Build development containers"
	@echo "  make build-prod     - Build production containers"
	@echo "  make up             - Start development containers"
	@echo "  make up-prod        - Start production containers"
	@echo "  make down           - Stop and remove containers"
	@echo "  make logs           - View container logs"
	@echo "  make clean          - Remove containers, volumes, and images"
	@echo "  make test           - Run tests in containers"
	@echo "  make shell-backend  - Open shell in backend container"
	@echo "  make shell-frontend - Open shell in frontend container"

# Build development containers
build:
	docker-compose build

# Build production containers
build-prod:
	docker-compose -f docker-compose.prod.yml build

# Start development containers
up:
	docker-compose up -d

# Start production containers
up-prod:
	docker-compose -f docker-compose.prod.yml up -d

# Stop containers
down:
	docker-compose down

# Stop production containers
down-prod:
	docker-compose -f docker-compose.prod.yml down

# View logs
logs:
	docker-compose logs -f

# View production logs
logs-prod:
	docker-compose -f docker-compose.prod.yml logs -f

# Clean up everything
clean:
	docker-compose down -v
	docker system prune -af

# Run tests
test:
	@echo "Running backend tests..."
	docker-compose run --rm backend python -m pytest
	@echo "Running frontend tests..."
	docker-compose run --rm frontend npm test

# Shell access
shell-backend:
	docker-compose exec backend /bin/bash

shell-frontend:
	docker-compose exec frontend /bin/sh

# Health check
health:
	@echo "Checking backend health..."
	@curl -f http://localhost:8000/api/v1/translate/health || echo "Backend is not healthy"
	@echo "\nChecking frontend health..."
	@curl -f http://localhost:3000/health || echo "Frontend is not healthy"

# Build and push for AWS App Runner
build-backend-prod:
	docker build -t medical-translator-backend:latest ./backend

build-frontend-prod:
	docker build -t medical-translator-frontend:latest ./frontend

# Development workflow
dev: build up logs

# Production workflow
prod: build-prod up-prod logs-prod