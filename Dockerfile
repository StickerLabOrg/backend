# Usar uma imagem base oficial do Python
FROM python:3.9-slim

# Instalar dependências do sistema, incluindo o cliente do postgres
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

# Definir o diretório de trabalho
WORKDIR /app

# Copiar o script de espera e dar permissão de execução
COPY wait-for-postgres.sh .
RUN chmod +x wait-for-postgres.sh

# Copiar o arquivo de dependências e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do código da aplicação
COPY . .

# Expor a porta que a aplicação vai rodar
EXPOSE 8000

# O comando para iniciar será definido no docker-compose.yml

# ============================
# Command to run the backend
# ============================
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
