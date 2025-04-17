## Makefile for setting up development environment and pre-commit hooks

.PHONY: help setup precommit

help:
	@echo "Available commands:"
	@echo "  make setup      Install dev dependencies and pre-commit hooks"
	@echo "  make precommit  Install pre-commit hooks only"

setup:
	@echo "Installing dev dependencies"
	uv pip install -e ".[dev]"
	@echo "Installing pre-commit"
	uv pip install pre-commit
	@echo "Installing pre-commit hooks"
	uv pre-commit install
	@echo "Running pre-commit on all files"
	uv pre-commit run --all-files

precommit:
	@echo "Installing pre-commit hooks"
	uv pre-commit install