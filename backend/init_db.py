import os
from sqlalchemy import create_engine, text

DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    print("DATABASE_URL not set")
    exit(1)

# Ensure postgresql:// instead of postgres:// 
if DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)

try:
    # Use isolation_level AUTOCOMMIT for CREATE EXTENSION
    engine = create_engine(DB_URL, isolation_level="AUTOCOMMIT")
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
    print("PostGIS extension ensured.")

    # Criação das tabelas
    import create_tables
    print("Iniciando verificação e criação de tabelas...")
    create_tables.create_all_tables()

    # A migração automatizada de dados legados do MySQL foi removida.
    # Os arquivos foram movidos para a pasta _legacy_archive na raiz do projeto.

    # 5. Carga de Geometrias dos Municípios (Polígonos IBGE)
    try:
        import seed_municipios_geom
        seed_municipios_geom.seed_municipios()
        print("Geometrias dos municípios sincronizadas.")
    except Exception as es:
        print(f"Erro ao carregar geometrias: {es}")

    # 6. Carga de Perímetros do CAR (Shapefiles) — REMOVIDO: Agora é Manual via API
    print("Nota: A carga de perímetros do CAR agora é manual via endpoint POST /api/v1/mapa/car/importar")

    # 7. Criação de Índices Espaciais
    try:
        import create_spatial_indexes
        create_spatial_indexes.create_indexes()
        # Índice adicional para CAR (caso não tenha sido criado pelo modelo)
        # criaremos no script de índices
        print("Índices espaciais criados.")
    except Exception as ei:
        print(f"Erro ao criar índices: {ei}")

    # 5. Criação das Views (Unificação de dados APP e Legado com Join Espacial)
    try:
        import create_views
        create_views.create_views()
        print("Views do banco de dados sincronizadas.")
    except Exception as ev:
        print(f"Erro ao sincronizar views: {ev}")

except Exception as e:
    print(f"Error creating extension or initializing db: {e}")
    exit(1)
