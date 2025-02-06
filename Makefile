# Makefile

# List of directories and files to format and lint
TARGETS = kronik/ tests/

# Run the tests
test:
	poetry run pytest -vv

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


# Display help message by default
.DEFAULT_GOAL := help
help:
	@echo "Available commands:"
	@echo "  make test        - Run the tests"
	@echo "  make format      - Format code using isort and black"
	@echo "  make lint        - Lint code using ruff"
	@echo "  make lint-fix    - Lint and fix code using ruff"

# Declare the targets as phony
.PHONY: test format lint lint-fix help
