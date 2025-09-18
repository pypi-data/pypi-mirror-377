check: format lint typecheck

format:
	uv run black . --check --diff

lint:
	uv run ruff check .

typecheck:
	uv run pyright

.PHONY: check format lint typecheck