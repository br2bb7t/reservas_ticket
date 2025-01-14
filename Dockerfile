FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=1.8.5

WORKDIR /app

# Instalar dependencias
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    pkg-config \
    libmariadb-dev \
    libpq-dev \
    libffi-dev \
    && apt-get clean

# Instalar Poetry 1.8.5
RUN curl -sSL https://install.python-poetry.org | python3 - --version 1.8.5 \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry \
    && poetry --version  # Verificar la instalación de Poetry

COPY pyproject.toml poetry.lock /app/

RUN poetry install --no-dev

COPY . /app/

CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
