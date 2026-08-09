# Makefile for MCP Test Project

.PHONY: help install test lint format typecheck clean run-server run-client

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install package in development mode
	pip install -e ".[dev]"

test:  ## Run tests with coverage
	pytest -v

lint:  ## Run linting (ruff)
	ruff check src tests

format:  ## Format code (ruff)
	ruff format src tests

typecheck:  ## Run type checking (mypy)
	mypy src

check: lint typecheck  ## Run all checks

clean:  ## Clean build artifacts
	rm -rf build dist *.egg-info .pytest_cache .coverage htmlcov .mypy_cache .ruff_cache

run-server:  ## Run the MCP server
	python -m mcp_test.server

run-client:  ## Run the MCP client (tests against server)
	python -m mcp_test.client