"""Teste direto do get_current_user"""
from app.config.database import SessionLocal
from app.models.user import SecUser
from app.utils.security import create_access_token
from app.schemas.user import UserWithPessoaResponse

# Criar token
token_data = {"sub": "admin"}
token = create_access_token(token_data)
print(f"Token criado: {token[:50]}...")

# Buscar usuário
db = SessionLocal()
user = db.query(SecUser).filter(SecUser.login == "admin").first()

if not user:
    print("❌ Usuário não encontrado!")
    exit(1)

print(f"\n✅ Usuário encontrado:")
print(f"   Login: {user.login}")
print(f"   Email: {user.email}")
print(f"   Name: {user.name}")
print(f"   Active: {user.active}")
print(f"   Type: {type(user)}")

# Tentar converter para schema
print(f"\n📋 Tentando converter para UserWithPessoaResponse...")
try:
    response = UserWithPessoaResponse.model_validate(user)
    print(f"✅ Conversão bem-sucedida!")
    print(f"   Response type: {type(response)}")
    print(f"   Response data: {response.model_dump()}")
except Exception as e:
    print(f"❌ Erro na conversão: {e}")
    import traceback
    traceback.print_exc()

db.close()
