# Dockerfile for mcp-jupyter-notebook
FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml .
COPY README.md .
COPY src/ ./src/

RUN pip install --upgrade pip && \
    pip install .

EXPOSE 8000

CMD ["mcp-jupyter-notebook"]
