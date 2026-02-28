.PHONY: install test lint format run-local-seo run-content run-competitor run-orchestrator clean

install:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

lint:
	@if command -v ruff >/dev/null 2>&1; then \
		ruff check .; \
	else \
		flake8 bots/ common/ infra/ tests/; \
	fi

format:
	black bots/ common/ infra/ tests/

run-local-seo:
	python -m bots.local_seo.run

run-content:
	python -m bots.content_creation.run

run-competitor:
	python -m bots.competitor_analysis.run

run-orchestrator:
	python -m bots.orchestrator.run

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	rm -rf .pytest_cache .ruff_cache dist *.egg-info
