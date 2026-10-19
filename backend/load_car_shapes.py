import os
import subprocess
import psycopg2
from dotenv import load_dotenv
import glob

def load_car_data(uf_filter: str = None):
    load_dotenv()
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL não encontrada.")
        return

    # Preparar conexão psycopg2
    temp_url = database_url.replace("postgresql+psycopg2://", "postgresql://")
    if temp_url.startswith("postgres://"):
        temp_url = temp_url.replace("postgres://", "postgresql://", 1)
    
    try:
        conn = psycopg2.connect(temp_url)
        conn.autocommit = True
        cur = conn.cursor()
        
        # 1. Garantir que a tabela final existe
        cur.execute("""
            CREATE TABLE IF NOT EXISTS car_propriedades (
                id SERIAL PRIMARY KEY,
                codigo_imovel VARCHAR(100) UNIQUE NOT NULL,
                tipo_imovel VARCHAR(50),
                situacao VARCHAR(50),
                municipio VARCHAR(255),
                sigla_uf VARCHAR(2),
                area_ha DOUBLE PRECISION,
                geom geometry(MULTIPOLYGON, 4326)
            );
            CREATE INDEX IF NOT EXISTS idx_car_propriedades_geom ON car_propriedades USING GIST (geom);
            CREATE INDEX IF NOT EXISTS idx_car_propriedades_uf ON car_propriedades (sigla_uf);
        """)

        # 2. Varredora de arquivos (com filtro de UF se fornecido)
        car_root = "/app/car"
        if uf_filter:
            pattern = os.path.join(car_root, uf_filter.upper(), "**", "*.shp")
            print(f"Buscando arquivos para UF: {uf_filter.upper()}")
        else:
            pattern = os.path.join(car_root, "**", "*.shp")
            print("Buscando arquivos para todas as UFs disponíveis...")
            
        shape_files = glob.glob(pattern, recursive=True)

        if not shape_files:
            print(f"Nenhum arquivo .shp encontrado em {car_root}")
            return

        # Para parsear a URL para o ogr2ogr
        clean_url = temp_url.replace("postgresql://", "")
        auth, rest = clean_url.split("@")
        user, password = auth.split(":")
        host_port, dbname = rest.split("/")
        host, port = host_port.split(":")
        pg_conn_str = f"PG:host={host} port={port} dbname={dbname} user={user} password={password}"

        for shp_path in shape_files:
            layer_name = os.path.splitext(os.path.basename(shp_path))[0]
            staging_table = f"stg_{layer_name.lower()}"
            
            print(f"Limpando staging {staging_table}...")
            cur.execute(f"DROP TABLE IF EXISTS {staging_table};")
            
            print(f"Importando {shp_path} para staging...")
            # Importa para uma tabela temporária de staging SEM restrições de unicidade
            cmd = [
                "ogr2ogr",
                "-f", "PostgreSQL",
                pg_conn_str,
                shp_path,
                "-nln", staging_table,
                "-t_srs", "EPSG:4326",
                "-nlt", "PROMOTE_TO_MULTI",
                "-lco", "GEOMETRY_NAME=geom",
                "-lco", "PRECISION=NO",
                "-skipfailures",
                "-sql", f"SELECT cod_imovel, ind_tipo, ind_status, municipio, CAST(num_area AS float) as num_area FROM {layer_name}"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Erro no ogr2ogr: {result.stderr}")
                continue

            print(f"Migrando dados de {staging_table} para car_propriedades (com tratamento de duplicados)...")
            # Agora migramos para a tabela oficial tratando conflitos de codigo_imovel
            cur.execute(f"""
                INSERT INTO car_propriedades (codigo_imovel, tipo_imovel, situacao, municipio, sigla_uf, area_ha, geom)
                SELECT cod_imovel, ind_tipo, ind_status, municipio, LEFT(cod_imovel, 2), num_area, geom
                FROM {staging_table}
                ON CONFLICT (codigo_imovel) DO NOTHING;
            """)
            print(f"Registros processados de {layer_name}: {cur.rowcount}")
            
            # Limpa staging
            cur.execute(f"DROP TABLE {staging_table};")

        cur.close()
        conn.close()
        print("Processo de carga do CAR finalizado com sucesso.")

    except Exception as e:
        print(f"Falha crítica na carga do CAR: {e}")

if __name__ == "__main__":
    load_car_data()
