from fastapi import APIRouter, Depends, Query, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config.database import get_db
from app.services.cache_service import cache_service
import json
import load_car_shapes

router = APIRouter(prefix="/api/v1/mapa/car", tags=["Mapa CAR"])

@router.get("")
async def get_car_properties(
    bbox: str = Query(None, description="minLat,minLon,maxLat,maxLon"),
    municipio_id: str = Query(None, description="Código IBGE do município (ex: 1501402)"),
    db: Session = Depends(get_db)
):
    """
    Retorna os perímetros do CAR.
    Funciona de duas formas:
    1. Se municipio_id for fornecido: Retorna todos os imóveis daquele município (Join Espacial).
    2. Se apenas BBox for fornecido: Retorna imóveis na área, com restrição de zoom (tamanho do BBox).
    """
    # Gerar chave de cache
    cache_key = f"mici:{municipio_id}" if municipio_id else f"bbox:{bbox}"
    
    # 1. Checar Cache Redis
    cached_geojson = cache_service.get_bbox_cache("car", cache_key)
    if cached_geojson:
        return cached_geojson

    # 2. Lógica de Seleção de Filtro
    if municipio_id:
        # Filtro por Município (Sugerido pelo usuário para performance)
        sql_query = """
            SELECT jsonb_build_object(
                'type', 'FeatureCollection',
                'features', COALESCE(jsonb_agg(features), '[]'::jsonb)
            )
            FROM (
                SELECT jsonb_build_object(
                    'type', 'Feature',
                    'id', cp.id,
                    'geometry', ST_AsGeoJSON(ST_SimplifyPreserveTopology(cp.geom, 0.0001))::jsonb,
                    'properties', jsonb_build_object(
                        'codigo_imovel', cp.codigo_imovel,
                        'situacao', cp.situacao,
                        'municipio', cp.municipio
                    )
                ) AS features
                FROM car_propriedades cp
                JOIN municipios m ON m.id = :mun_id
                WHERE ST_Intersects(cp.geom, m.geom)
            ) AS subquery
        """
        params = {"mun_id": municipio_id}
    
    elif bbox:
        # Filtro por BBox (com proteção de área)
        try:
            min_lat, min_lon, max_lat, max_lon = map(float, bbox.split(","))
        except ValueError:
            raise HTTPException(status_code=400, detail="BBox inválido.")

        bbox_area = (max_lat - min_lat) * (max_lon - min_lon)
        
        # Proteção: Não exibir CAR em áreas muito grandes sem filtro de município
        if bbox_area > 0.2: 
            return {
                "type": "FeatureCollection",
                "features": [],
                "warning": "Habilite o filtro por município ou aproxime o mapa para ver os dados do CAR."
            }
            
        sql_query = """
            SELECT jsonb_build_object(
                'type', 'FeatureCollection',
                'features', COALESCE(jsonb_agg(features), '[]'::jsonb)
            )
            FROM (
                SELECT jsonb_build_object(
                    'type', 'Feature',
                    'id', id,
                    'geometry', ST_AsGeoJSON(ST_SimplifyPreserveTopology(geom, 0.00005))::jsonb,
                    'properties', jsonb_build_object(
                        'codigo_imovel', codigo_imovel,
                        'situacao', situacao
                    )
                ) AS features
                FROM car_propriedades
                WHERE geom && ST_MakeEnvelope(:min_lon, :min_lat, :max_lon, :max_lat, 4326)
                LIMIT 2000
            ) AS subquery
        """
        params = {
            "min_lat": min_lat, "min_lon": min_lon, 
            "max_lat": max_lat, "max_lon": max_lon
        }
    else:
        return {"type": "FeatureCollection", "features": [], "message": "Forneça municipio_id ou bbox."}

    # 3. Executar e Cachear
    try:
        result = db.execute(text(sql_query), params).scalar()
        if result:
            cache_service.set_bbox_cache("car", cache_key, result)
            return result
        return {"type": "FeatureCollection", "features": []}
    except Exception as e:
        print(f"Erro CAR: {e}")
        raise HTTPException(status_code=500, detail="Erro interno na consulta espacial.")

@router.post("/importar")
async def importar_car(
    background_tasks: BackgroundTasks,
    uf: str = Query(None, description="Sigla da UF para importar (ex: PA). Se vazio, tenta todas.")
):
    """
    Dispara a importação de Shapefiles do CAR para o banco de dados.
    A operação é executada em segundo plano.
    """
    background_tasks.add_task(load_car_shapes.load_car_data, uf)
    return {
        "status": "success",
        "message": f"Importação de dados do CAR ({uf if uf else 'Todas as UFs'}) iniciada em segundo plano. Acompanhe os logs do servidor para o progresso."
    }
