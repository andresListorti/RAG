FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app/src
WORKDIR /app
RUN groupadd --gid 10001 app && useradd --uid 10001 --gid app --create-home app
COPY pyproject.toml uv.lock README.md ./
RUN pip install --no-cache-dir uv==0.12.15 && uv sync --frozen --no-dev --no-install-project
COPY src ./src
COPY data ./data
COPY web ./web
USER app
EXPOSE 8000
CMD ["/app/.venv/bin/uvicorn", "consumidor.api:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
