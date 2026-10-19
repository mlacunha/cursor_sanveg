import json
import os
import psycopg2
from dotenv import load_dotenv
import glob

def seed_municipios():
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

        # 1. Garantir coluna geom em municipios
        cur.execute("""
            ALTER TABLE municipios 
            ADD COLUMN IF NOT EXISTS geom geometry(MULTIPOLYGON, 4326);
        """)
        print("Coluna geom garantida na tabela municípios.")

        # 2. Encontrar todos os arquivos GeoJSON
        # Ajustar o path para refletir a estrutura do projeto
        search_path = os.path.join("app", "data", "geojs-*-mun.json")
        files = glob.glob(search_path)
        
        if not files:
            # Tentar path alternativo caso esteja sendo rodado de fora da pasta api
            search_path = os.path.join("api", "app", "data", "geojs-*-mun.json")
            files = glob.glob(search_path)

        if not files:
            print(f"Nenhum arquivo GeoJSON encontrado em {search_path}")
            return

        print(f"Encontrados {len(files)} arquivos GeoJSON para processar.")

        total_updated = 0
        for file_path in files:
            print(f"Processando {file_path}...")
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for feature in data.get('features', []):
                ibge_id = feature['properties'].get('id')
                if not ibge_id:
                    continue
                
                # Converter geometria para WKT ou GeoJSON para o PostGIS
                # ST_GeomFromGeoJSON é perfeito aqui
                geom_json = json.dumps(feature['geometry'])
                
                # Tentar atualizar pelo ID (que é o código IBGE)
                cur.execute("""
                    UPDATE municipios 
                    SET geom = ST_Multi(ST_GeomFromGeoJSON(%s))
                    WHERE id = %s
                """, (geom_json, int(ibge_id)))
                
                if cur.rowcount > 0:
                    total_updated += 1

        print(f"Concluído. Geometrias atualizadas: {total_updated}")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Erro no seed de municípios: {e}")

if __name__ == "__main__":
    seed_municipios()
