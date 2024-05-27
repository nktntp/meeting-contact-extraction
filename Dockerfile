FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11-slim

RUN pip install poetry==1.8.3

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false

RUN poetry install --without test

COPY . /app