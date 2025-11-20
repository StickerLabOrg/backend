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
#   Dependencies (runtime + dev)
# ============================
COPY requirements.txt requirements-dev.txt ./

RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

# ============================
#   Copy application code
# ============================
COPY . .

# Script de espera pelo PostgreSQL
COPY wait-for-postgres.sh .
RUN chmod +x wait-for-postgres.sh


ENV PYTHONPATH=/app

# ============================
#   Expose API
# ============================
EXPOSE 8000

# ============================
#   CMD (não roda testes aqui)
#   Testes são rodados no docker-compose
# ============================
CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload"]
