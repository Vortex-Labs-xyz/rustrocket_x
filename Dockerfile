# ––––– Build Stage –––––
FROM python:3.12-slim AS build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VIRTUALENVS_IN_PROJECT=false

# System-Abhängigkeiten
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        build-essential \
        gcc \
    && rm -rf /var/lib/apt/lists/*

# Poetry installieren
RUN curl -sSL https://install.python-poetry.org | python -
ENV PATH="/root/.local/bin:$PATH"

# Arbeitsverzeichnis
WORKDIR /app

# Projekt-Metadaten kopieren und Abhängigkeiten installieren
COPY pyproject.toml poetry.lock* README.md /app/
COPY rustrocket_x/ /app/rustrocket_x/
RUN poetry install --no-interaction --no-ansi --only main

# Quellcode kopieren
COPY . /app



# ––––– Runtime Stage –––––
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Abhängigkeiten und App übernehmen
COPY --from=build /usr/local /usr/local
COPY --from=build /app /app

WORKDIR /app

# Default-Entrypoint
CMD ["python", "-m", "rustrocket_x"] 