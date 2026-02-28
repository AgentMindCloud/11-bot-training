.PHONY: install test lint run-seo run-content run-competitor run-orchestrator

install:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

lint:
	ruff check . --fix

run-seo:
	python -m bots.local_seo.run

run-content:
	python -m bots.content.run

run-competitor:
	python -m bots.competitor.run

run-orchestrator:
	python -m bots.orchestrator.run
