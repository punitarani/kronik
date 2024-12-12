# Makefile

# List of directories and files to format and lint
TARGETS = kronik/ tests/

# Format code using isort and black
format:
	poetry run isort $(TARGETS)
	poetry run black $(TARGETS)

# Lint code using ruff
lint:
	poetry run ruff check $(TARGETS)

# Lint and fix code using ruff
lint-fix:
	poetry run ruff check --fix $(TARGETS)

# Setup project for development
setup:
	poetry run pre-commit install --config .config/.pre-commit.yaml
	poetry run pre-commit autoupdate --config .config/.pre-commit.yaml


# Display help message by default
.DEFAULT_GOAL := help
help:
	@echo "Available commands:"
	@echo "  make format      - Format code using isort and black"
	@echo "  make lint        - Lint code using ruff"
	@echo "  make check       - Format and lint code"

# Declare the targets as phony
.PHONY: format lint check help
