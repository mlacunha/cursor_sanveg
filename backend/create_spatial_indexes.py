import psycopg2
import os
from dotenv import load_dotenv

def create_indexes():
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL não encontrada.")
        return

    if database_url.startswith("postgresql+psycopg2://"):
        database_url = database_url.replace("postgresql+psycopg2://", "postgresql://")

    try:
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cur = conn.cursor()

        print("Criando índices espaciais GIST...")

        # Índice para municípios
        cur.execute("CREATE INDEX IF NOT EXISTS idx_municipios_geom ON municipios USING GIST (geom);")
        print("Índice idx_municipios_geom criado.")

        # Índice para relatorio_mapa
        cur.execute("CREATE INDEX IF NOT EXISTS idx_relatorio_mapa_geom ON relatorio_mapa USING GIST (geom);")
        print("Índice idx_relatorio_mapa_geom criado.")

        # Índice para area_inspecionada
        cur.execute("CREATE INDEX IF NOT EXISTS idx_area_inspecionada_geom ON area_inspecionada USING GIST (geom);")
        print("Índice idx_area_inspecionada_geom criado.")

        # Índice para car_propriedades
        cur.execute("CREATE INDEX IF NOT EXISTS idx_car_propriedades_geom ON car_propriedades USING GIST (geom);")
        print("Índice idx_car_propriedades_geom criado.")

        print("Todos os índices espaciais foram garantidos.")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Erro ao criar índices espaciais: {e}")

if __name__ == "__main__":
    create_indexes()
