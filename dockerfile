# Gunakan image Python yang ringan
FROM python:3.11-slim

# Tentukan direktori kerja
WORKDIR /app

# Copy daftar library dan install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh kode FastAPI/MCP kamu
COPY . .

# Jalankan server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]