FROM python:3.13-slim

# Pasang tool uv ke dalam container
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvbin/uv
ENV PATH="/uvbin:$PATH"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /mcp-linkedin

# Copy file dependensi (biar kalau ganti kode, install-nya tidak ulang)
COPY pyproject.toml uv.lock ./

# Install semua library (Basic uv sync)
RUN uv sync --frozen --no-dev

# Copy semua kodingan
COPY . .

EXPOSE 8000

# Jalankan uvicorn lewat uv run agar otomatis masuk ke environment-nya
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]