# 🚀 Deploy em 3 Passos

## 1️⃣ Preparar ZIP

Execute no terminal:
```bash
python prepare_deploy.py
```

Arquivo criado: `svegpa-api-deploy.zip`

---

## 2️⃣ Configurar no Painel

### Criar Aplicação Python

- **Name**: `svegpa-api`
- **Python**: `3.13.0`
- **Diretório**: `/home/svegpa-api`
- **Script**:
  ```bash
  pip install -r requirements.txt && gunicorn -k uvicorn.workers.UvicornWorker main:app --bind=0.0.0.0:8080
  ```
- **Porta App**: `8080`
- **Porta Externa**: `8083`
- **Acesso Externo**: ✅

### Adicionar Variáveis

```
DATABASE_URL = postgresql://sanveg:xD5MhfGRknjz8hZQ@209.50.227.136:5432/sanveg
SECRET_KEY = e9f2c1b7d5a8f4e0c3b6a9d0c3f6a5d8e1f4a7b0c3d6e9f2a5b8c1d4e7f0a3b6
ACCESS_TOKEN_EXPIRE_MINUTES = 1440
SMTP_SERVER = svegpa.org
SMTP_PORT = 587
SMTP_USERNAME = naoresponda@svegpa.org
SMTP_PASSWORD = SenhaForte@2025
EMAIL_FROM_ADDRESS = naoresponda@svegpa.org
```

---

## 3️⃣ Upload e Iniciar

1. Upload `svegpa-api-deploy.zip`
2. Extrair arquivos
3. Clicar "Confirmar"
4. Aguardar 2-3 minutos

---

## ✅ Testar

Acesse: `http://seu-dominio:8083/docs`

Login de teste:
```json
{
  "email": "admin@admin.com",
  "password": "admin123"
}
```

---

## 📚 Documentação Completa

- **Checklist detalhado**: `CHECKLIST_DEPLOY.md`
- **Guia completo**: `DEPLOY_RAPIDO.md`
- **Deploy avançado**: `DEPLOY.md`

---

## 🎯 URLs da API

- Docs: `/docs`
- ReDoc: `/redoc`
- Health: `/health`
- OpenAPI: `/openapi.json`

**Total**: 71 endpoints
