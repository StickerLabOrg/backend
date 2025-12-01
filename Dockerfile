# ============================
#   Base Image
# ============================
FROM python:3.9-slim

# ============================
#   System dependencies
# ============================
RUN apt-get update && apt-get install -y \
    build-essential \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# ============================
#   App directory
# ============================
WORKDIR /app

# ============================
#   Dependencies (APENAS PRODUÇÃO)
# ============================
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# ============================
#   Copy wait script
# ============================
COPY wait-for-postgres.sh /app/wait-for-postgres.sh
RUN chmod +x /app/wait-for-postgres.sh

# ============================
#   Copy application code
# ============================
COPY . .

ENV PYTHONPATH=/app

# ============================
#   Expose API
# ============================
EXPOSE 8000

# ============================
#   CMD (sem --reload em produção)
# ============================
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
