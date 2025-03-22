.PHONY: clean install dev test lint format docs build dist help

help:
	@echo "LLM Directory Organizer Development Commands"
	@echo ""
	@echo "Usage:"
	@echo "  make <command>"
	@echo ""
	@echo "Commands:"
	@echo "  install    Install the package"
	@echo "  dev        Install development dependencies"
	@echo "  clean      Remove build artifacts"
	@echo "  test       Run tests"
	@echo "  lint       Run code linting"
	@echo "  format     Format code with black"
	@echo "  docs       Build documentation"
	@echo "  build      Build package distribution files"
	@echo "  dist       Build and upload package to PyPI"

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

install:
	pip install -e .

dev:
	pip install -r requirements-dev.txt

test:
	pytest --cov=llm_organizer tests/

lint:
	flake8 src/llm_organizer
	mypy src/llm_organizer
	isort --check-only --profile black src/llm_organizer

format:
	black src/llm_organizer tests
	isort --profile black src/llm_organizer tests

docs:
	sphinx-build -b html docs/source docs/build

build: clean
	python -m build

dist: build
	twine check dist/*
	@echo "To upload to PyPI, run: twine upload dist/*"
