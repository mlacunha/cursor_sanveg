# SVEGPA API - FastAPI

API desenvolvida em FastAPI para integração com WeWeb.io e FlutterFlow.io

## Estrutura do Projeto

```
api_svegpa/
├── app/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   └── settings.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── pessoa.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── user.py
│   ├── routers/
│   │   ├── __init__.py
│   │   └── auth.py
│   └── utils/
│       ├── __init__.py
│       ├── security.py
│       └── email.py
├── main.py
├── requirements.txt
├── .env
├── .env.example
└── README.md
```

## Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/mlacunha/svegpa_api_fastapi.git
cd api_svegpa
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv
```

### 3. Ative o ambiente virtual

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
.\venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

### 5. Configure as variáveis de ambiente

Copie o arquivo `.env.example` para `.env` e configure as variáveis:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações.

## Executar a API

```bash
uvicorn main:app --reload
```

A API estará disponível em: `http://localhost:8000`

Documentação interativa: `http://localhost:8000/docs`

## Endpoints

### Autenticação

- **POST** `/api/auth/login` - Login com email e senha
- **GET** `/api/auth/me` - Obter dados do usuário autenticado (WeWeb)
- **POST** `/api/auth/change-password` - Alterar senha do usuário logado
- **POST** `/api/auth/forgot-password` - Solicitar reset de senha
- **POST** `/api/auth/reset-password` - Resetar senha com token

## Banco de Dados

- **SGBD:** PostgreSQL 16+
- **Extensão Espacial:** PostGIS (Essencial para inteligência geográfica)
- **Servidor:** 209.50.227.136
- **Porta:** 5432
- **Database:** sanveg
- **Diferencial Geográfico:** O SVEGPA utiliza PostGIS para realizar cruzamentos espaciais avançados, como a verificação automática de pontos de inspeção dentro de polígonos de municípios e integração com perímetros do CAR (Cadastro Ambiental Rural).

## Tecnologias

- FastAPI
- SQLAlchemy
- PostGIS / GeoAlchemy2
- JWT (python-jose)
- Pydantic
- Bcrypt

## Licença

Privado
