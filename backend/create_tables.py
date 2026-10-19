"""
Script de inicialização do banco de dados appsinfo_sanveg_v1.
Cria todas as tabelas definidas nos modelos SQLAlchemy.

Uso:
    cd sanvegFastAPI
    python create_tables.py
"""

import sys
from pathlib import Path

# Garante que o diretório raiz do projeto está no path
sys.path.insert(0, str(Path(__file__).parent))

from app.config.database import engine, Base
from app.config.settings import get_settings

# Importa todos os modelos (registra no metadata do Base)
import app.models  # noqa: F401 — side-effect import

settings = get_settings()


def create_all_tables():
    print(f"\n{'='*60}")
    print(f"  Banco de dados : {settings.DB_NAME}")
    print(f"  Host           : {settings.DB_HOST}:{settings.DB_PORT}")
    print(f"  Usuário        : {settings.DB_USER}")
    print(f"{'='*60}\n")

    tabelas = list(Base.metadata.tables.keys())
    print(f"  Tabelas a criar ({len(tabelas)}):")
    for t in sorted(tabelas):
        print(f"    - {t}")
    print()

    try:
        # Configurações específicas podem ser adicionadas aqui
        Base.metadata.create_all(
            bind=engine,
            checkfirst=True,
        )
        print("[OK]  Todas as tabelas foram criadas com sucesso!\n")
    except Exception as e:
        print(f"[ERRO]  {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    create_all_tables()
