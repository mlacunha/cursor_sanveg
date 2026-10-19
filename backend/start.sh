#!/bin/bash

# Script de inicialização para deploy em VPS

echo "🚀 Iniciando SVEGPA API..."

# Ativar ambiente virtual se existir
if [ -d "venv" ]; then
    echo "📦 Ativando ambiente virtual..."
    source venv/bin/activate
fi

# Verificar se arquivo .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  Arquivo .env não encontrado!"
    echo "📋 Copiando .env.example para .env..."
    cp .env.example .env
    echo "✏️  Por favor, edite o arquivo .env com as configurações corretas!"
    exit 1
fi

# Instalar dependências se necessário
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📥 Instalando dependências..."
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# Iniciar aplicação
echo "✅ Iniciando servidor..."
if command -v gunicorn &> /dev/null; then
    # Produção com Gunicorn
    gunicorn -k uvicorn.workers.UvicornWorker main:app \
        --bind 0.0.0.0:8080 \
        --workers 4 \
        --access-logfile - \
        --error-logfile - \
        --log-level info
else
    # Desenvolvimento com Uvicorn
    uvicorn main:app --host 0.0.0.0 --port 8080 --reload
fi
