FROM ghcr.io/astral-sh/uv:0.8.15-debian-slim

WORKDIR /code

COPY ./pyproject.toml /code/pyproject.toml

COPY ./uv.lock /code/uv.lock

COPY ./.python-version /code/.python-version

RUN uv sync --locked

ENV PORT=80

COPY ./app /code/app

CMD ["uv", "run", "fastapi", "run", "app/main.py", "--proxy-headers"]