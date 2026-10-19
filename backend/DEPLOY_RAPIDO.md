# 🚀 Deploy Rápido - SVEGPA API em VPS com Painel ICP

## 📦 Preparação dos Arquivos

### 1. Criar arquivo ZIP para upload

Exclua estas pastas antes de compactar:
- `venv/`
- `__pycache__/`
- `.git/`
- `logs/`

Compacte todos os outros arquivos em `svegpa-api.zip`

---

## 🎯 Configuração no Painel ICP

### Passo 1: Criar Aplicação Python

**No menu lateral, vá em:** `Aplicações > Python > Standalone`

Clique em **"Criar"**

### Passo 2: Configurar Aplicação

| Campo | Valor |
|-------|-------|
| **Name** | `svegpa-api` |
| **Aplicação** | `Python 3.13.0` |
| **Diretório** | `/home/svegpa-api` |
| **Script de Execução** | `pip install -r requirements.txt && gunicorn -k uvicorn.workers.UvicornWorker main:app --bind=0.0.0.0:8080` |
| **Porta da Aplicação** | `8080` |
| **Porta Externa** | `8083` |
| **Acesso externo** | ✅ Ativado |

### Passo 3: Variáveis de Ambiente

Adicione as seguintes variáveis (conforme imagens):

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

### Passo 4: Upload dos Arquivos

1. Clique no botão **"Escolher arquivo"** ou use o gerenciador de arquivos
2. Faça upload do `svegpa-api.zip`
3. Extraia os arquivos no diretório `/home/svegpa-api`

### Passo 5: Iniciar Aplicação

1. Clique em **"Confirmar"** para salvar as configurações
2. A aplicação iniciará automaticamente
3. Aguarde 1-2 minutos para instalação das dependências

---

## ✅ Verificação

### Testar a API

Acesse no navegador:

```
http://seu-dominio.vps5908.panel:8083/docs
```

Ou pelo domínio configurado:

```
https://api.svegpa.org/docs
```

### Endpoints de Teste

**Health Check:**
```
GET http://seu-dominio:8083/api/health
```

**Login:**
```
POST http://seu-dominio:8083/api/auth/login
Content-Type: application/json

{
  "email": "admin@admin.com",
  "password": "admin123"
}
```

---

## 📊 Monitoramento

### Visualizar Logs

No painel:
1. Vá em `Logs`
2. Selecione a aplicação `svegpa-api`
3. Visualize logs em tempo real

### Reiniciar Aplicação

No painel:
1. Vá na lista de aplicações Python
2. Clique no botão de **Restart** ao lado de `svegpa-api`

---

## 🔧 Comandos Úteis

### Atualizar Código

1. Faça upload do novo arquivo ZIP
2. Extraia sobrescrevendo os arquivos
3. Reinicie a aplicação no painel

### Atualizar Dependências

No terminal SSH (se disponível):
```bash
cd /home/svegpa-api
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

Ou adicione ao script de execução:
```bash
pip install -r requirements.txt --upgrade && gunicorn...
```

---

## 🌐 Configurar Domínio Personalizado

### Opção 1: Subdomínio

1. Crie um registro A/CNAME no DNS:
   - Nome: `api`
   - Tipo: `A`
   - Valor: `IP do servidor`

2. No painel ICP, adicione domínio:
   - Vá em `Web > Domínios`
   - Adicione `api.svegpa.org`
   - Configure proxy reverso para `localhost:8083`

### Opção 2: Usar Proxy Reverso

Configure no Apache/Nginx do painel:

**Apache (.htaccess):**
```apache
ProxyPass /api http://localhost:8083
ProxyPassReverse /api http://localhost:8083
```

**Nginx:**
```nginx
location /api {
    proxy_pass http://localhost:8083;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

---

## 🔒 Segurança - IMPORTANTE!

### Antes de usar em produção:

- [ ] Altere `SECRET_KEY` para valor único
- [ ] Configure `DEBUG=False`
- [ ] Ative HTTPS (SSL/TLS)
- [ ] Configure CORS para domínios específicos
- [ ] Adicione rate limiting
- [ ] Configure backup automático do banco
- [ ] Monitore logs de erro

---

## 📱 Acesso pela API

### Base URL

**Desenvolvimento:**
```
http://vps5908.panel:8083
```

**Produção:**
```
https://api.svegpa.org
```

### Autenticação

Todos os endpoints (exceto login) requerem token JWT:

```http
Authorization: Bearer seu-token-aqui
```

---

## 🐛 Troubleshooting

### Erro 500 - Internal Server Error

**Verifique:**
1. Logs da aplicação
2. Variáveis de ambiente configuradas
3. Conexão com banco de dados

### Erro 502 - Bad Gateway

**Causa:** Aplicação não está rodando

**Solução:**
1. Reinicie a aplicação no painel
2. Verifique se a porta 8080 está livre
3. Veja logs para erros de inicialização

### Erro de Importação de Módulos

**Causa:** Dependências não instaladas

**Solução:**
```bash
pip install -r requirements.txt
```

### Banco de Dados Não Conecta

**Verifique:**
1. IP do servidor liberado no PostgreSQL
2. Credenciais corretas
3. Firewall não bloqueando porta 3306

---

## 📞 Contato

Para suporte técnico:
- 📧 Email: suporte@svegpa.org
- 📱 WhatsApp: (91) 98765-4321

---

## 🎉 Pronto!

Sua API está rodando em:
- Docs: http://seu-dominio:8083/docs
- ReDoc: http://seu-dominio:8083/redoc
- Total de endpoints: **71**
