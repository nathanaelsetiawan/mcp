FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /mcp-server

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project
COPY . .

EXPOSE 5001
CMD ["uv", "run", "python", "main.py"]