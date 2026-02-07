.PHONY: tests_unit tests_integration
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

tests_unit:
	uv run pytest -vvvvv --html=tests_unit_report.html --self-contained-html tests_unit

tests_unit_specific:
	uv run pytest -vvvvv --setup-show --html=tests_unit_specific_report.html --self-contained-html tests_unit/middleware/test_request_id.py::test_new_request_id_when_not_supplied_in_request

tests_integration:
	uv run pytest -vvvvv --html=tests_integration_report.html --self-contained-html tests_integration

tests_integration_specific:
	uv run pytest -vvvvv --setup-show --html=tests_integration_specific_report.html --self-contained-html tests_integration/test_main.py::test_root_get

upgrade:
	uv sync --upgrade

ruff:
	uv run ruff check --fix
	uv run ruff format

flake8:
	uv run flake8 --ignore=E501 --exclude=.venv,.git # ignore max line length

run_all:
	make init ruff flake8 tests_unit tests_integration

docker_compose_pull:
	docker compose -f docker-compose.yml pull

docker_compose_start:
	docker compose -f docker-compose.yml up --build -d

docker_compose_stop:
	docker compose -f docker-compose.yml down -v

docker_compose_restart:
	make docker_compose_stop docker_compose_start

fast_dev_docker_compose_restart:
	make docker_compose_restart fast_dev

docker:
	docker build --pull -t python-fastapi -f Dockerfile .