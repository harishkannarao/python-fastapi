.DEFAULT_GOAL := run_all

init:
	uv sync --locked

init_dependencies:
	uv sync

init_ci:
	pip install uv --upgrade
	uv sync --locked

fast_dev:
	uv run fastapi dev app/main.py

fast_run:
	uv run fastapi run app/main.py

upgrade:
	uv sync --upgrade

ruff:
	uv run ruff check
	uv run ruff format

flake8:
	uv run flake8 --ignore=E501 --exclude=.venv,.git # ignore max line length

run_all:
	make init ruff flake8

docker:
	docker build --pull -t python-fastapi -f Dockerfile .