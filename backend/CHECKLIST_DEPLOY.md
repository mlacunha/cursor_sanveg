# 📋 Checklist de Deploy - Painel ICP

Use este checklist enquanto configura a aplicação no painel.

## ✅ Preparação Local

- [ ] Executar `python prepare_deploy.py` para criar ZIP
- [ ] Verificar arquivo `svegpa-api-deploy.zip` criado
- [ ] Arquivo ZIP tem aproximadamente 2-5 MB

---

## ✅ Configuração no Painel - Aba Principal

### Informações Básicas

- [ ] **Name**: `svegpa-api`
- [ ] **Aplicação**: `Python 3.13.0` selecionado
- [ ] **Diretório**: `/home/svegpa-api` ou `/home/seu-usuario/svegpa-api`

### Script de Execução

Copie e cole exatamente:

```bash
pip install -r requirements.txt && gunicorn -k uvicorn.workers.UvicornWorker main:app --bind=0.0.0.0:8080
```

- [ ] Script colado corretamente
- [ ] Sem quebras de linha extras

### Portas

- [ ] **Porta da Aplicação**: `8080`
- [ ] **Porta Externa**: `8083` (ou sua preferência)
- [ ] **Acesso externo**: ✅ **ATIVADO**

### Container

- [ ] **Nome do Container**: `svegpa-api`

---

## ✅ Variáveis de Ambiente

Adicione cada variável clicando em "Adicionar":

### Variável 1
- [ ] **Variável**: `DATABASE_URL`
- [ ] **Valor**: `postgresql://sanveg:xD5MhfGRknjz8hZQ@209.50.227.136:5432/sanveg`

### Variável 2
- [ ] **Variável**: `SECRET_KEY`
- [ ] **Valor**: `e9f2c1b7d5a8f4e0c3b6a9d0c3f6a5d8e1f4a7b0c3d6e9f2a5b8c1d4e7f0a3b6`

### Variável 3
- [ ] **Variável**: `ACCESS_TOKEN_EXPIRE_MINUTES`
- [ ] **Valor**: `1440`

### Variável 4
- [ ] **Variável**: `SMTP_SERVER`
- [ ] **Valor**: `svegpa.org`

### Variável 5
- [ ] **Variável**: `SMTP_PORT`
- [ ] **Valor**: `587`

### Variável 6
- [ ] **Variável**: `SMTP_USERNAME`
- [ ] **Valor**: `naoresponda@svegpa.org`

### Variável 7
- [ ] **Variável**: `SMTP_PASSWORD`
- [ ] **Valor**: `SenhaForte@2025`

### Variável 8
- [ ] **Variável**: `EMAIL_FROM_ADDRESS`
- [ ] **Valor**: `naoresponda@svegpa.org`

**Total de variáveis**: 8

---

## ✅ Upload e Extração

- [ ] Clicar em área de upload ou botão "Escolher arquivo"
- [ ] Selecionar `svegpa-api-deploy.zip`
- [ ] Aguardar upload completar (barra de progresso 100%)
- [ ] Arquivo aparece na lista
- [ ] Extrair arquivo no diretório configurado
- [ ] Verificar estrutura de pastas criada

---

## ✅ Configurações Avançadas (Opcional)

Se disponível no painel:

### NanoCPU
- [ ] Deixar em `0` (ilimitado) ou ajustar conforme necessidade

### Memória
- [ ] Deixar em `0` (ilimitado) ou mínimo `512 MB`

---

## ✅ Inicialização

- [ ] Clicar em **"Confirmar"** para salvar
- [ ] Aguardar mensagem de sucesso
- [ ] Aplicação inicia automaticamente
- [ ] Aguardar 1-3 minutos para instalação de dependências

---

## ✅ Verificação

### Logs
- [ ] Acessar aba "Logs" da aplicação
- [ ] Verificar mensagens de inicialização
- [ ] Sem erros críticos visíveis
- [ ] Mensagem "Application startup complete" presente

### Teste de Acesso

Abrir no navegador (substitua com seu domínio):

- [ ] `http://vps5908.panel:8083/health` retorna JSON
- [ ] `http://vps5908.panel:8083/docs` abre Swagger UI
- [ ] `http://vps5908.panel:8083/api/health` retorna status healthy

Resposta esperada do `/health`:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

## ✅ Teste Funcional

### Login
- [ ] Abrir `http://seu-dominio:8083/docs`
- [ ] Expandir `POST /api/auth/login`
- [ ] Clicar em "Try it out"
- [ ] Usar credenciais de teste:
  ```json
  {
    "email": "admin@admin.com",
    "password": "admin123"
  }
  ```
- [ ] Clicar "Execute"
- [ ] Resposta 200 OK com token JWT
- [ ] Copiar token do response

### Autorização
- [ ] Clicar no botão "Authorize" (cadeado no topo)
- [ ] Colar token no formato: `Bearer seu-token-aqui`
- [ ] Clicar "Authorize"
- [ ] Clicar "Close"

### Teste de Endpoint Protegido
- [ ] Expandir `GET /api/auth/me`
- [ ] Clicar "Try it out"
- [ ] Clicar "Execute"
- [ ] Resposta 200 OK com dados do usuário

---

## ✅ Finalização

- [ ] Todos os testes passaram
- [ ] Aplicação respondendo corretamente
- [ ] Logs sem erros críticos
- [ ] Documentação acessível

---

## 🐛 Troubleshooting

### ❌ Erro 500 ao acessar

**Verificar:**
- [ ] Logs da aplicação no painel
- [ ] Todas as variáveis de ambiente configuradas
- [ ] Valores das variáveis sem espaços extras
- [ ] Arquivo .env foi criado ou variáveis no painel

**Solução:**
1. Revisar variáveis de ambiente
2. Reiniciar aplicação
3. Verificar logs novamente

### ❌ Erro 502 Bad Gateway

**Causa:** Aplicação não iniciou

**Verificar:**
- [ ] Script de execução correto
- [ ] Porta 8080 configurada
- [ ] requirements.txt existe
- [ ] Logs de instalação de dependências

**Solução:**
1. Reiniciar aplicação no painel
2. Verificar logs de erro
3. Confirmar Python 3.13.0 selecionado

### ❌ Dependências não instalam

**Verificar logs para:**
- [ ] Erro de permissão
- [ ] Falta de espaço em disco
- [ ] Versão Python incorreta

**Solução:**
1. Verificar versão Python selecionada
2. Limpar cache: adicionar `--no-cache-dir` ao pip install
3. Atualizar pip: adicionar `pip install --upgrade pip &&` antes do comando

### ❌ Banco de dados não conecta

**Verificar:**
- [ ] IP do servidor VPS liberado no PostgreSQL remoto
- [ ] Credenciais corretas em DATABASE_URL
- [ ] Porta 3306 acessível
- [ ] Firewall não bloqueando conexão

**Teste manual:**
```bash
PostgreSQL -h 209.50.227.136 -u sanveg -p -P 3306 sanveg
```

---

## 📞 Suporte

Se encontrar problemas:

1. **Consulte logs** primeiro
2. **Verifique checklist** novamente
3. **Leia** `DEPLOY_RAPIDO.md`
4. **Contate** suporte técnico se necessário

---

## ✨ Deploy Concluído!

Sua API está rodando em:

- **Docs**: http://seu-dominio:8083/docs
- **ReDoc**: http://seu-dominio:8083/redoc
- **Health**: http://seu-dominio:8083/health

**Total de endpoints disponíveis:** 71

🎉 **Parabéns!** A API SVEGPA está no ar!
