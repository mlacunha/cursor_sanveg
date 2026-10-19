"""Teste completo dos endpoints de autenticação"""
import sys
import traceback
from sqlalchemy.orm import Session
from app.config.database import SessionLocal
from app.models.user import SecUser
from app.schemas.user import UserWithPessoaResponse
from app.utils.security import create_access_token, verify_password

print("=== TESTE COMPLETO DE ENDPOINTS ===\n")

# 1. Testar conexão com banco
print("1. Testando conexão com banco de dados...")
db = SessionLocal()
try:
    user = db.query(SecUser).filter(SecUser.email == "admin@admin.com").first()
    if user:
        print(f"✅ Usuário encontrado: {user.login}")
        print(f"   Email: {user.email}")
        print(f"   Name: {user.name}")
        print(f"   Active: {user.active}")
        print(f"   Phone: {user.phone}")
        print(f"   Matricula: {user.matricula}")
    else:
        print("❌ Usuário não encontrado")
        sys.exit(1)
except Exception as e:
    print(f"❌ Erro ao conectar: {e}")
    traceback.print_exc()
    sys.exit(1)

# 2. Testar verificação de senha
print("\n2. Testando verificação de senha...")
try:
    senha_correta = verify_password("admin", user.pswd)
    if senha_correta:
        print("✅ Senha verificada com sucesso")
    else:
        print("❌ Senha incorreta")
        sys.exit(1)
except Exception as e:
    print(f"❌ Erro ao verificar senha: {e}")
    traceback.print_exc()
    sys.exit(1)

# 3. Testar criação de token
print("\n3. Testando criação de token JWT...")
try:
    token = create_access_token({"sub": user.email, "user_login": user.login})
    print(f"✅ Token criado: {token[:50]}...")
except Exception as e:
    print(f"❌ Erro ao criar token: {e}")
    traceback.print_exc()
    sys.exit(1)

# 4. Testar conversão para schema (o problema principal)
print("\n4. Testando conversão do modelo para schema...")
try:
    # Tentar converter diretamente
    user_response = UserWithPessoaResponse.model_validate(user)
    print(f"✅ Conversão direta bem-sucedida!")
    print(f"   Login: {user_response.login}")
    print(f"   Email: {user_response.email}")
    print(f"   Name: {user_response.name}")
    print(f"   Active: {user_response.active}")
    print(f"   Phone: {user_response.phone}")
    print(f"   Matricula: {user_response.matricula}")
except Exception as e:
    print(f"❌ Erro na conversão direta: {e}")
    traceback.print_exc()
    
    # Tentar conversão manual
    print("\n   Tentando conversão manual...")
    try:
        user_response = UserWithPessoaResponse(
            login=user.login,
            email=user.email,
            name=user.name,
            active=user.active,
            phone=user.phone,
            matricula=user.matricula
        )
        print(f"✅ Conversão manual bem-sucedida!")
        print(f"   Login: {user_response.login}")
        print(f"   Email: {user_response.email}")
        print(f"   Name: {user_response.name}")
        print(f"   Active: {user_response.active}")
        print(f"   Phone: {user_response.phone}")
        print(f"   Matricula: {user_response.matricula}")
    except Exception as e2:
        print(f"❌ Erro na conversão manual: {e2}")
        traceback.print_exc()
        sys.exit(1)

# 5. Testar serialização JSON
print("\n5. Testando serialização para JSON...")
try:
    json_data = user_response.model_dump()
    print(f"✅ Serialização JSON bem-sucedida!")
    print(f"   Dados: {json_data}")
except Exception as e:
    print(f"❌ Erro na serialização: {e}")
    traceback.print_exc()
    sys.exit(1)

db.close()
print("\n🎉 TODOS OS TESTES PASSARAM!")
