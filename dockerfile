FROM python:3.13-slim

# Pasang tool uv ke dalam container
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvbin/uv
ENV PATH="/uvbin:$PATH"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /mcp-linkedin

# GUNAKAN TRIK INI: Copy pyproject.toml dan uv.lock secara eksplisit
# Tanda * membantu jika ada karakter aneh atau masalah context
COPY pyproject.toml ./
COPY uv.lock ./

# Jika uv.lock tetap tidak terbaca, kita pastikan uv melakukan sinkronisasi
# --frozen tetap dipakai agar versi akurat sesuai lockfile
RUN uv sync --frozen --no-dev

# Copy semua kodingan
COPY . .

EXPOSE 8000

# Jalankan uvicorn lewat uv run
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]