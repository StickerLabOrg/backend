# 🖥️ Backend - Projeto Álbum de Figurinhas

Este repositório contém o **backend** do projeto, desenvolvido em **FastAPI (Python)**.
O backend é responsável por disponibilizar a **API REST** para o frontend e gerenciar dados do banco.

-----

## 🚀 Tecnologias Utilizadas

  - [FastAPI](https://fastapi.tiangolo.com/)
  - [Uvicorn](https://www.uvicorn.org/)
  - [SQLAlchemy](https://www.sqlalchemy.org/) (ou Prisma Python, caso definido)
  - [Docker](https://www.docker.com/)
  - Banco de Dados: **ainda em definição** (PostgreSQL ou MySQL recomendados)

## 📂 Estrutura do Projeto

```
backend/
│── app/
│   ├── main.py       # Entrada principal
│   ├── routes/       # Rotas da API
│   ├── models/       # Modelos do banco
│   ├── services/     # Lógica de negócio
│   └── schemas/      # Validações
│── tests/            # Testes automatizados
└── Dockerfile
```

-----

## ⚙️ Instalação e Execução

### Pré-requisitos

  - Python \>= 3.10
  - Docker (opcional)

### Rodando localmente

```bash
# Clone o repositório
git clone https://github.com/ORG_NAME/backend.git
cd backend

# Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação
uvicorn app.main:app --reload
```

### Rodando com Docker

```bash
# Construa a imagem Docker
docker build -t album-backend .

# Execute o container
docker run -p 8000:8000 album-backend
```

### ✅ Testes

```bash
pytest
```

### 📦 Deploy

O deploy será feito em servidor (AWS/Render/Heroku), rodando em container Docker.

-----

## 📄 Licença

