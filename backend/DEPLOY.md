# Guia de Deploy - API SVEGPA

## 📋 Pré-requisitos

- VPS com painel ICP (cPanel ou similar)
- Python 3.13.0 disponível
- Acesso ao gerenciador de arquivos
- Acesso ao banco de dados PostgreSQL já configurado

## 🚀 Passo a Passo para Deploy

### 1. Upload dos Arquivos

1. **Compactar o projeto**:
   - Compacte todos os arquivos do projeto em um arquivo `.zip`
   - Exclua as pastas: `venv`, `__pycache__`, `.git`

2. **Upload via Gerenciador de Arquivos**:
   - Acesse o painel ICP
   - Vá em "Aplicações" > "Python" > "Standalone"
   - Ou use o gerenciador de arquivos para criar a pasta `/home/usuario/api_svegpa`
   - Faça upload do arquivo `.zip`
   - Extraia os arquivos

### 2. Configuração no Painel ICP

#### Configuração da Aplicação Python

**Nome**: `svegpa-api`

**Aplicação**: `Python 3.13.0`

**Diretório**: `/home/seu-usuario/api_svegpa`

**Script de Execução**:
```
pip install -r requirements.txt && gunicorn -k uvicorn.workers.UvicornWorker main:app --bind=0.0.0.0:$PORT
```

**Porta da Aplicação**: `8080` (porta interna)

**Porta Externa**: `8083` (ou a que preferir)

**Acesso Externo**: ✅ Ativado

#### Variáveis de Ambiente

Configure as seguintes variáveis no painel:

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

### 3. Instalação de Dependências

No terminal do painel (se disponível) ou via SSH temporário:

```bash
cd /home/seu-usuario/api_svegpa
python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Configuração do Ambiente

1. **Copiar arquivo de configuração**:
   ```bash
   cp .env.example .env
   ```

2. **Editar `.env`** via gerenciador de arquivos com as credenciais corretas

### 5. Testar a Aplicação

1. No painel ICP, inicie a aplicação
2. Verifique os logs em "Logs" > "api_svegpa.log"
3. Acesse: `http://seu-dominio:8083/docs`
4. Teste o endpoint de health: `http://seu-dominio:8083/api/health`

### 6. Configuração de Domínio (Opcional)

Se quiser usar um domínio ou subdomínio:

1. No painel, vá em "Web" > "Domínios"
2. Crie um subdomínio: `api.svegpa.org`
3. Configure proxy reverso para porta `8083`:
   - Origem: `http://localhost:8083`
   - Destino: `https://api.svegpa.org`

## 🔧 Comandos Úteis

### Via Painel Python Runtime

**Instalar dependências**:
```bash
pip install -r requirements.txt
```

**Atualizar dependências**:
```bash
pip install --upgrade -r requirements.txt
```

**Ver logs**:
- Acesse "Logs" no painel da aplicação

## 📝 Estrutura de Arquivos no Servidor

```
/home/seu-usuario/api_svegpa/
├── app/
│   ├── config/
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   └── utils/
├── main.py
├── requirements.txt
├── .env
├── passenger_wsgi.py
├── .htaccess
└── runtime.txt
```

## ⚠️ Troubleshooting

### Aplicação não inicia

1. Verifique os logs da aplicação
2. Confirme que todas as variáveis de ambiente estão configuradas
3. Verifique se o Python 3.13.0 está selecionado
4. Confirme que todas as dependências foram instaladas

### Erro de conexão com banco de dados

1. Verifique se o IP do servidor está liberado no PostgreSQL remoto
2. Confirme as credenciais em `.env`
3. Teste conexão manual via PostgreSQL client

### Erro 502 Bad Gateway

1. Verifique se a porta está correta
2. Confirme que a aplicação está rodando
3. Verifique logs de erro

### CORS Issues

- Já configurado no `main.py` para aceitar todas as origens em desenvolvimento
- Para produção, ajuste `allow_origins` no middleware CORS

## 🔒 Segurança

### Antes do Deploy em Produção:

1. **Altere** `SECRET_KEY` para um valor único e seguro
2. **Configure** `DEBUG=False` no `.env`
3. **Restrinja** CORS para apenas domínios autorizados
4. **Ative** HTTPS no domínio
5. **Configure** firewall para bloquear portas desnecessárias
6. **Revise** todas as senhas e credenciais

## 📞 Suporte

Para problemas ou dúvidas:
- Verifique logs da aplicação
- Consulte documentação do FastAPI: https://fastapi.tiangolo.com
- Documentação do painel ICP/cPanel

## 🎯 Endpoints Principais

Após deploy, a API estará disponível em:

- **Documentação**: `http://seu-dominio:8083/docs`
- **ReDoc**: `http://seu-dominio:8083/redoc`
- **OpenAPI JSON**: `http://seu-dominio:8083/openapi.json`

### Endpoints de Autenticação:
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Dados do usuário
- `POST /api/auth/change-password` - Trocar senha
- `POST /api/auth/forgot-password` - Recuperar senha
- `POST /api/auth/reset-password` - Resetar senha

### CRUDs Disponíveis:
- `/api/orgaos-tipos/`
- `/api/orgaos/`
- `/api/unidades/`
- `/api/cargos/`
- `/api/programas/`
- `/api/hospedeiros/`
- `/api/normas/`
- `/api/users/` (admin only)
- `/api/produtores/`
- `/api/propriedades/`
- `/api/termo-inspecao/`
- `/api/amostra-coletada/`

Total: **71 endpoints** disponíveis
