# 📚 Documentação de Deploy - SVEGPA API

## 📁 Arquivos Criados para Deploy

### Arquivos de Configuração

| Arquivo | Descrição |
|---------|-----------|
| `requirements.txt` | Dependências Python atualizadas com gunicorn |
| `.env.example` | Template de variáveis de ambiente com valores de produção |
| `runtime.txt` | Versão do Python (3.13.0) |
| `Procfile` | Configuração para Heroku/Cloud platforms |
| `passenger_wsgi.py` | Arquivo WSGI para Passenger (cPanel/ICP) |
| `.htaccess` | Configuração Apache para Passenger |
| `gunicorn.conf.py` | Configuração do Gunicorn para produção |
| `.gitignore` | Arquivos ignorados pelo Git (atualizado) |

### Scripts Auxiliares

| Arquivo | Descrição |
|---------|-----------|
| `prepare_deploy.py` | Script para criar ZIP de deploy automaticamente |
| `start.sh` | Script de inicialização para Linux/Unix |

### Documentação

| Arquivo | Descrição | Quando Usar |
|---------|-----------|-------------|
| `DEPLOY_3_PASSOS.md` | Resumo super rápido | Início rápido |
| `CHECKLIST_DEPLOY.md` | Checklist detalhado passo a passo | Durante configuração |
| `DEPLOY_RAPIDO.md` | Guia completo simplificado | Referência principal |
| `DEPLOY.md` | Guia técnico completo | Troubleshooting avançado |
| `README_DEPLOY.md` | Este arquivo | Visão geral |

---

## 🚀 Fluxo de Deploy Recomendado

### 1. Preparação Local (5 min)

```bash
# Executar script de preparação
python prepare_deploy.py
```

**Resultado:** Arquivo `svegpa-api-deploy.zip` criado (~2-5 MB)

**O que o script faz:**
- Exclui `venv`, `__pycache__`, `.git`, logs
- Compacta apenas arquivos necessários
- Mostra estatísticas do ZIP criado

---

### 2. Upload no Painel (3 min)

**Navegação:** `Aplicações > Python > Standalone > Criar`

**Configurações Básicas:**
```
Name: svegpa-api
Python: 3.13.0
Diretório: /home/svegpa-api
Porta App: 8080
Porta Externa: 8083
Acesso Externo: ✅
```

**Script de Execução:**
```bash
pip install -r requirements.txt && gunicorn -k uvicorn.workers.UvicornWorker main:app --bind=0.0.0.0:8080
```

---

### 3. Configurar Variáveis (2 min)

**Essenciais (8 variáveis):**

| Variável | Valor |
|----------|-------|
| `DATABASE_URL` | `postgresql://sanveg:xD5MhfGRknjz8hZQ@209.50.227.136:5432/sanveg` |
| `SECRET_KEY` | `e9f2c1b7d5a8f4e0c3b6a9d0c3f6a5d8e1f4a7b0c3d6e9f2a5b8c1d4e7f0a3b6` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` |
| `SMTP_SERVER` | `svegpa.org` |
| `SMTP_PORT` | `587` |
| `SMTP_USERNAME` | `naoresponda@svegpa.org` |
| `SMTP_PASSWORD` | `SenhaForte@2025` |
| `EMAIL_FROM_ADDRESS` | `naoresponda@svegpa.org` |

---

### 4. Iniciar e Verificar (5 min)

1. **Confirmar** configurações no painel
2. **Aguardar** instalação de dependências (1-3 min)
3. **Verificar logs** - procurar por "Application startup complete"
4. **Testar** endpoints:

```bash
# Health check
curl http://seu-dominio:8083/health

# Resposta esperada:
{
  "status": "healthy",
  "version": "1.0.0"
}
```

5. **Acessar docs**: `http://seu-dominio:8083/docs`

---

## ✅ Testes Funcionais

### Teste 1: Login

**Endpoint:** `POST /api/auth/login`

**Payload:**
```json
{
  "email": "admin@admin.com",
  "password": "admin123"
}
```

**Resposta esperada:** `200 OK` com token JWT

---

### Teste 2: Endpoint Protegido

**Endpoint:** `GET /api/auth/me`

**Headers:**
```
Authorization: Bearer {seu-token-jwt}
```

**Resposta esperada:** `200 OK` com dados do usuário

---

### Teste 3: CRUD Básico

**Endpoint:** `GET /api/orgaos-tipos/`

**Resposta esperada:** `200 OK` com lista de tipos de órgãos

---

## 📊 Estrutura da API

### Estatísticas

- **Total de Endpoints:** 71
- **Routers:** 13
- **Modelos de Banco:** 12
- **Schemas Pydantic:** 36+
- **Autenticação:** JWT Bearer Token
- **Expiração Token:** 1440 minutos (24 horas)

### Endpoints por Categoria

| Categoria | Quantidade | Prefixo |
|-----------|------------|---------|
| Autenticação | 5 | `/api/auth/` |
| Órgãos Tipos | 5 | `/api/orgaos-tipos/` |
| Órgãos | 5 | `/api/orgaos/` |
| Unidades | 5 | `/api/unidades/` |
| Cargos | 5 | `/api/cargos/` |
| Programas | 5 | `/api/programas/` |
| Hospedeiros | 5 | `/api/hospedeiros/` |
| Normas | 5 | `/api/normas/` |
| Usuários | 5 | `/api/users/` |
| Produtores | 5 | `/api/produtores/` |
| Propriedades | 5 | `/api/propriedades/` |
| Termo Inspeção | 5 | `/api/termo-inspecao/` |
| Amostra Coletada | 5 | `/api/amostra-coletada/` |
| Health Check | 1 | `/health` |

---

## 🔒 Segurança Implementada

### Autenticação
- ✅ JWT com expiração configurável
- ✅ Senha hash com bcrypt
- ✅ Migração automática MD5 → bcrypt
- ✅ Tokens de recuperação de senha

### Autorização
- ✅ Proteção de rotas com `Depends(get_current_user)`
- ✅ Rotas admin-only com `Depends(get_admin_user)`
- ✅ Validação de permissões em tempo real

### CORS
- ✅ Configurado para aceitar qualquer origem (desenvolvimento)
- ⚠️ **ATENÇÃO:** Restringir em produção!

### Validação
- ✅ Pydantic schemas para todos os endpoints
- ✅ Validação de email
- ✅ Validação de tipos de dados
- ✅ Validação de campos obrigatórios

---

## 🛠️ Funcionalidades Especiais

### 1. Controle Sequencial
- Auto-incremento de `ficha_inspecao`
- Auto-incremento de `termo_coleta`
- Por usuário e ano

### 2. Campos Geográficos
- Suporte a coordenadas POINT (PostgreSQL)
- Conversão automática lat/long → POINT
- Visualização com `ST_AsText()`

### 3. Chaves Compostas
- Suporte completo para PKs compostas
- Exemplo: `amostra_coletada` (id_termo + id)

### 4. Triggers de Banco
- Auto-geração de IDs em `amostra_coletada`
- Geração automática de campos calculados

### 5. Relacionamentos Opcionais
- FKs não obrigatórias retornam dados quando disponíveis
- Não geram erro se vazias/nulas
- Usa `joinedload()` do SQLAlchemy

---

## 📱 Integração com Frontends

### WeWeb.io

**Base URL:** `https://api.svegpa.org` ou `http://dominio:8083`

**Autenticação:**
1. Fazer login: `POST /api/auth/login`
2. Armazenar token JWT
3. Incluir em headers: `Authorization: Bearer {token}`

**Exemplo de integração:**
```javascript
// Login
const response = await fetch('https://api.svegpa.org/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
});
const { access_token } = await response.json();

// Usar token
const data = await fetch('https://api.svegpa.org/api/produtores/', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
```

### FlutterFlow.io

**API Group:** SVEGPA API

**Endpoints configurados:**
- Login: `POST /api/auth/login`
- Me: `GET /api/auth/me`
- Todos os CRUDs disponíveis

**Headers padrão:**
```
Content-Type: application/json
Authorization: Bearer [Variable]
```

---

## 🔧 Manutenção

### Atualizar Código

1. Fazer alterações localmente
2. Testar localmente
3. Executar `python prepare_deploy.py`
4. Upload novo ZIP
5. Extrair sobrescrevendo
6. Reiniciar aplicação no painel

### Atualizar Dependências

Editar `requirements.txt` e adicionar ao script de execução:

```bash
pip install -r requirements.txt --upgrade && gunicorn...
```

### Backup

**Banco de Dados:**
```bash
PostgreSQLdump -h 209.50.227.136 -u sanveg -p sanveg > backup.sql
```

**Arquivos:**
- Download via gerenciador de arquivos
- Ou compactar e baixar via FTP

### Logs

**Visualizar:**
1. Painel > Logs > svegpa-api
2. Ou via terminal: `tail -f /home/usuario/logs/api_svegpa.log`

---

## 🐛 Troubleshooting Comum

### Aplicação não inicia

**Verificar:**
1. Logs da aplicação
2. Variáveis de ambiente
3. Versão Python selecionada
4. requirements.txt existe

**Solução:**
```bash
# Verificar logs
cat /home/usuario/logs/api_svegpa.log

# Reinstalar dependências
pip install -r requirements.txt --force-reinstall
```

### Erro 502 Bad Gateway

**Causa:** Aplicação não está respondendo

**Soluções:**
1. Reiniciar no painel
2. Verificar porta 8080 livre
3. Confirmar script de execução correto

### Banco não conecta

**Verificar:**
1. IP liberado no PostgreSQL remoto
2. Credenciais corretas
3. Porta 3306 acessível

**Teste:**
```bash
PostgreSQL -h 209.50.227.136 -u sanveg -p -P 3306 sanveg
```

### CORS Error

**Solução temporária:** Já configurado para aceitar todas as origens

**Solução produção:** Editar `main.py`:
```python
allow_origins=["https://seu-dominio.com"]
```

---

## 📞 Suporte

### Documentação
- FastAPI: https://fastapi.tiangolo.com
- SQLAlchemy: https://docs.sqlalchemy.org
- Pydantic: https://docs.pydantic.dev

### Logs Importantes
- `/home/usuario/logs/api_svegpa.log`
- Logs do painel ICP
- Logs do navegador (F12)

---

## ✨ Status do Projeto

### ✅ Implementado

- [x] 13 routers (auth + 12 CRUDs)
- [x] 71 endpoints funcionais
- [x] Autenticação JWT completa
- [x] Recuperação de senha
- [x] Sistema de permissões admin
- [x] Controle sequencial (ficha_inspecao, termo_coleta)
- [x] Suporte a campos geográficos POINT
- [x] Chaves compostas
- [x] Relacionamentos opcionais
- [x] Documentação automática (Swagger/ReDoc)
- [x] Health check endpoint
- [x] CORS configurado
- [x] Validação completa com Pydantic
- [x] Arquivos de deploy preparados

### 🎯 Pronto para Deploy

- [x] requirements.txt atualizado
- [x] Configurações de produção
- [x] Scripts de inicialização
- [x] Documentação completa
- [x] Testes manuais realizados
- [x] SMTP configurado

---

## 🎉 Deploy Checklist

- [ ] Preparar ZIP com `prepare_deploy.py`
- [ ] Criar aplicação Python no painel
- [ ] Configurar 8 variáveis de ambiente
- [ ] Upload e extrair ZIP
- [ ] Confirmar e aguardar inicialização
- [ ] Testar `/health` endpoint
- [ ] Testar login via `/docs`
- [ ] Verificar logs sem erros
- [ ] Configurar domínio personalizado (opcional)
- [ ] Restringir CORS para produção
- [ ] Alterar DEBUG=False
- [ ] Configurar backup automático
- [ ] Monitorar logs por 24h

---

**Versão da API:** 1.0.0  
**Última atualização:** 19/11/2025  
**Python:** 3.13.0  
**FastAPI:** 0.115.5
