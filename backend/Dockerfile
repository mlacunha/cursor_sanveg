FROM python:3.12-slim-bookworm

WORKDIR /app

# Instalar dependências nativas vitais para psycopg2, GeoAlchemy2, Shapely e WeasyPrint/pycairo compilarem
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libgdal-dev \
    gdal-bin \
    libgeos-dev \
    libproj-dev \
    binutils \
    libcairo2-dev \
    pkg-config \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Configurar variáveis de ambiente necessárias para o GDAL compile do Shapely
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Copiar o arquivo de dependências
COPY requirements.txt .

# Atualizar o pip e instalar setuptools e wheel previamente
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante da aplicação para o diretório de trabalho
COPY . .

# Variáveis de ambiente úteis
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expor a porta em que a aplicação roda
EXPOSE 8080

# Comando para iniciar a aplicação via shell script que inicializa o DB
CMD ["sh", "-c", "python init_db.py && gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8080"]
