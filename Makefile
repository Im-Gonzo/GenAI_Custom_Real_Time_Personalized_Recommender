.PHONY: format lint install clean help check-env

# Colors for terminal output
BLUE := \033[1;34m
NC := \033[0m # No Color
GREEN := \033[1;32m
RED := \033[1;31m
YELLOW := \033[1;33m

# Python settings
PYTHON := python3
VENV := .venv
PIP := $(VENV)/bin/pip

help:
	@echo "$(BLUE)Available commands:$(NC)"
	@echo "$(GREEN)make install$(NC)      - Install all dependencies using poetry"
	@echo "$(GREEN)make format$(NC)       - Format code using ruff"
	@echo "$(GREEN)make check$(NC)        - Check code format without making changes"
	@echo "$(GREEN)make lint$(NC)         - Run linting checks"
	@echo "$(GREEN)make clean$(NC)        - Clean up cache and build files"
	@echo "$(GREEN)make check-env$(NC)    - Verify environment variables"

install:
	@echo "$(BLUE)Installing project dependencies...$(NC)"
	poetry install

format:
	@echo "$(BLUE)Formatting code with ruff...$(NC)"
	poetry run ruff format .
	@echo "$(BLUE)Organizing imports...$(NC)"
	poetry run ruff check --select I --fix .
	@echo "$(GREEN)Formatting complete!$(NC)"

check:
	@echo "$(BLUE)Checking code format...$(NC)"
	poetry run ruff format . --check
	poetry run ruff check --select I .

lint:
	@echo "$(BLUE)Running linting checks...$(NC)"
	poetry run ruff check .
	@echo "$(GREEN)Linting complete!$(NC)"

clean:
	@echo "$(BLUE)Cleaning up...$(NC)"
	rm -rf .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "$(GREEN)Clean up complete!$(NC)"

check-env:
	@echo "$(BLUE)Checking environment variables...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(RED)Error: .env file not found$(NC)"; \
		echo "$(YELLOW)Please create .env file from .env.example$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Environment file exists.$(NC)"
	@$(PYTHON) -c 'from recsys.config import settings; print("Environment variables loaded successfully!")'

# Development task groups
dev-setup: install check-env
	@echo "$(GREEN)Development environment setup complete!$(NC)"

dev-check: format lint
	@echo "$(GREEN)Code checks complete!$(NC)"