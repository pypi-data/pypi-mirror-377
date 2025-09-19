# Makefile for mcp-jupyter-notebook

.PHONY: install test lint run clean

install:
	pip install -e .

test:
	pytest tests/

lint:
	ruff src/

run:
	mcp-jupyter-notebook

clean:
	rm -rf __pycache__ .pytest_cache *.pyc *.pyo *.pyd *.egg-info build dist
