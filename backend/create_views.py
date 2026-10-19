import psycopg2
import os
from dotenv import load_dotenv

def create_views():
    load_dotenv()
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL não encontrada no .env")
        return

    # Ajustar dialeto para psycopg2 se necessário (SQLAlchemy usa postgresql+psycopg2)
    if database_url.startswith("postgresql+psycopg2://"):
        database_url = database_url.replace("postgresql+psycopg2://", "postgresql://")

    try:
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cur = conn.cursor()

        print("Criando/Atualizando View: vw_mapa_levantamentos...")

        view_sql = """
        CREATE OR REPLACE VIEW vw_levantamentos AS
        -- PARTE 1: DADOS LEGADOS (RELATORIO_MAPA)
        SELECT 
            p.nome::TEXT AS nome_programa, 
            rm.id_programa::TEXT AS id_programa,  
            EXTRACT(YEAR FROM rm.data::DATE)::TEXT AS ano, 
            EXTRACT(QUARTER FROM rm.data::DATE)::INTEGER AS trimestre,  
            COALESCE(mun.nome, rm.municipio)::TEXT AS municipio, 
            COALESCE(prop.nome, '')::TEXT AS nome_propriedade,   
            rm.tipo_imovel::TEXT AS tipo_imovel, 
            rm.cultura::TEXT AS cultura, 
            ST_Y(rm.geom)::FLOAT AS latitude, 
            ST_X(rm.geom)::FLOAT AS longitude,
            UPPER(COALESCE(rm.status, 'NORMAL'))::TEXT AS status, 
            rm.data::DATE AS data, 
            COALESCE(prop."UF", 'PA')::TEXT AS uf, 
            'legado'::TEXT AS fonte,
            rm.geom AS geom,
            rm.id::TEXT AS id,
            mun.id AS municipio_id
        FROM relatorio_mapa rm
        LEFT JOIN programas p ON p.id = rm.id_programa
        LEFT JOIN propriedades prop ON prop.id = rm.id_propriedade
        LEFT JOIN municipios mun ON ST_Intersects(rm.geom, mun.geom)
        WHERE rm.geom IS NOT NULL

        UNION ALL 

        -- PARTE 2: NOVAS INSPEÇÕES (APP)
        SELECT 
            prog.nome::TEXT AS nome_programa,
            prog.id::TEXT AS id_programa,
            EXTRACT(YEAR FROM ti.data)::TEXT AS ano,
            EXTRACT(QUARTER FROM ti.data)::INTEGER AS trimestre,
            COALESCE(mun.nome, prop.municipio)::TEXT AS municipio,
            COALESCE(prop.nome, '')::TEXT AS nome_propriedade,
            NULL::TEXT AS tipo_imovel,
            ap.especie::TEXT AS cultura,
            ST_Y(ai.geom)::FLOAT AS latitude,
            ST_X(ai.geom)::FLOAT AS longitude,
            UPPER(COALESCE(ap.resultado, 'NORMAL'))::TEXT AS status,
            ti.data::DATE AS data,
            COALESCE(prop."UF", 'PA')::TEXT AS uf, 
            'app'::TEXT AS fonte,
            ai.geom AS geom,
            ai.id::TEXT AS id,
            mun.id AS municipio_id
        FROM area_programa ap
        JOIN area_inspecionada ai ON ai.id = ap.id_area
        JOIN termo_inspecao ti ON ti.id = ai.id_termo_inspecao
        JOIN programas prog ON prog.id = ap.id_programa
        LEFT JOIN propriedades prop ON prop.id = ti.id_propriedade
        LEFT JOIN municipios mun ON ST_Intersects(ai.geom, mun.geom)
        WHERE ai.geom IS NOT NULL;
        """

        cur.execute(view_sql)
        print("View vw_levantamentos criada com sucesso!")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Erro ao criar views: {e}")

if __name__ == "__main__":
    create_views()
