# Como Executar a API

## 1. Ativar o Ambiente Virtual

```powershell
.\venv\Scripts\Activate.ps1
```

## 2. Executar a API

```powershell
uvicorn main:app --reload
```

Ou usando Python:

```powershell
python main.py
```

## 3. Acessar a Documentação

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 4. Testar os Endpoints

### Login (FlutterFlow)
```bash
POST http://localhost:8000/api/auth/login
Content-Type: application/json

{
  "email": "usuario@example.com",
  "pswd": "senha123"
}
```

### Me - Obter dados do usuário (WeWeb)
```bash
GET http://localhost:8000/api/auth/me
Authorization: Bearer {seu_token_jwt}
```

### Alterar Senha
```bash
POST http://localhost:8000/api/auth/change-password
Authorization: Bearer {seu_token_jwt}
Content-Type: application/json

{
  "current_password": "senha_atual",
  "new_password": "nova_senha",
  "confirm_password": "nova_senha"
}
```

### Esqueci Senha
```bash
POST http://localhost:8000/api/auth/forgot-password
Content-Type: application/json

{
  "email": "usuario@example.com"
}
```

### Reset Senha
```bash
POST http://localhost:8000/api/auth/reset-password
Content-Type: application/json

{
  "token": "token_recebido_por_email",
  "new_password": "nova_senha",
  "confirm_password": "nova_senha"
}
```

## Sincronizar com GitHub

Para fazer push das alterações:

```powershell
git add .
git commit -m "Sua mensagem de commit"
git push -u origin main
```

## Notas Importantes

1. Configure o arquivo `.env` com as credenciais corretas antes de executar
2. Para produção, altere o `SECRET_KEY` no `.env`
3. Configure as credenciais de SMTP para envio de emails
4. As tabelas `sec_users` e `pessoas` devem existir no banco de dados PostgreSQL
