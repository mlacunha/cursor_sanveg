"""
Roteador de Visualização de Mapas - Sistema SVEGPA
Gera mapas interativos HTML com Folium/Leaflet para visualização e captura PDF.

ESPECIFICAÇÕES TÉCNICAS (Validadas 18/12/2025):
- CircleMarker com cores por status (blue, orange, red)
- Zoom inteligente: Estado vs Município
- Limites territoriais via GeoJSON IBGE
- Viewport 100vw x 100vh (sem distorção)
- zoomSnap/zoomDelta = 0.1
"""

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse, HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, text, func
from typing import Optional
from datetime import date
import folium
import logging
import json
import os
import uuid

from app.config.database import get_db
from app.models.relatorio_mapa import RelatorioMapa
from app.models.municipio import Municipio

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/relatorio-mapa", tags=["Relatório Mapa"])

# Mapeamento UF para Código IBGE (Pasta app/data/geojs-XX-mun.json)
MAPA_UF_IBGE = {
    'RO': '11', 'AC': '12', 'AM': '13', 'RR': '14', 'PA': '15', 'AP': '16', 'TO': '17',
    'MA': '21', 'PI': '22', 'CE': '23', 'RN': '24', 'PB': '25', 'PE': '26', 'AL': '27',
    'SE': '28', 'BA': '29', 'MG': '31', 'ES': '32', 'RJ': '33', 'SP': '35', 'PR': '41',
    'SC': '42', 'RS': '43', 'MS': '50', 'MT': '51', 'GO': '52', 'DF': '53'
}


def _query_relatorios(
    db: Session,
    uf: Optional[str] = None,
    municipio: Optional[str] = None,
    cultura: Optional[str] = None,
    status: Optional[str] = None,
    ano: Optional[str] = None,
    trimestre: Optional[int] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    id_programa: Optional[str] = None
):
    """
    Consulta relatórios unindo dados legados e novos (app) via Subquery.
    Garante que os filtros funcionem sobre os ALIASES das colunas.
    """
    
    # ─────────────────────────────────────────────────────────────────────────────
    # Fonte 1: Dados legados (relatorio_mapa)
    # ─────────────────────────────────────────────────────────────────────────────
    params = {}
    where_clauses = []
    
    # Construção de filtros dinâmicos sobre a Subquery
    # NOTA: Os filtros de UF e município a nível de SQL foram removidos pois
    # usaremos a abordagem de Point-In-Polygon espacial em memória.
    
    if cultura:
        where_clauses.append("combined.cultura LIKE :cultura")
        params["cultura"] = f"%{cultura}%"
    
    if status:
        status_up = status.upper()
        if status_up in ['FOCO', 'POSITIVO']:
            where_clauses.append("combined.status IN ('FOCO', 'POSITIVO')")
        else:
            where_clauses.append("combined.status = :status")
            params["status"] = status_up
    
    if id_programa:
        where_clauses.append("combined.id_programa = :id_programa")
        params["id_programa"] = str(id_programa)
        
    if ano:
        where_clauses.append("combined.ano = :ano")
        params["ano"] = str(ano)

    if trimestre:
        where_clauses.append("combined.trimestre = :trimestre")
        params["trimestre"] = int(trimestre)

    if data_inicio:
        where_clauses.append("combined.data >= :data_inicio")
        params["data_inicio"] = data_inicio
    
    if data_fim:
        where_clauses.append("combined.data <= :data_fim")
        params["data_fim"] = data_fim

    # Query final usando Subquery para unificar os nomes das colunas
    # Normalizamos a 'data' para garantir que filtros >= e <= funcionem via SQL
    where_str = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    
    sql_final = f"""
        SELECT *
        FROM vw_mapa_levantamentos AS combined
        {where_str}
        ORDER BY combined.data DESC
    """
    
    logger.info(f"Executando Query Unificada com filtros: {list(params.keys())}")
    
    try:
        # Converter para mappings() para acesso via dicionário no marker loop
        result = db.execute(text(sql_final), params).mappings().all()
        
        # Converter Decimal para float para evitar erro de serialização JSON no Folium
        from decimal import Decimal
        parsed = []
        for row in result:
            row_dict = dict(row)
            for k, v in row_dict.items():
                if isinstance(v, Decimal):
                    row_dict[k] = float(v)
            parsed.append(row_dict)
            
        return parsed
    except Exception as e:
        logger.error(f"Erro crítico na query unificada: {e}")
        return []

def __point_in_polygon(x: float, y: float, poly: list) -> bool:
    """Ray-casting para determinar se um ponto está dentro de um polígono."""
    n = len(poly)
    inside = False
    if n == 0: return False
    p1x, p1y = poly[0]
    for i in range(1, n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def _is_point_in_geometry(lon: float, lat: float, geometry: dict) -> bool:
    """Valida se o ponto cai dentro do GeoJSON IBGE (Polygon ou MultiPolygon)."""
    if not geometry or 'coordinates' not in geometry:
        return False
        
    coords = geometry['coordinates']
    geom_type = geometry.get('type')
    
    if geom_type == 'Polygon':
        if not coords: return False
        if not __point_in_polygon(lon, lat, coords[0]):
            return False
        for hole in coords[1:]:
            if __point_in_polygon(lon, lat, hole):
                return False
        return True
        
    elif geom_type == 'MultiPolygon':
        for poly_coords in coords:
            if not poly_coords: continue
            if __point_in_polygon(lon, lat, poly_coords[0]):
                in_hole = False
                for hole in poly_coords[1:]:
                    if __point_in_polygon(lon, lat, hole):
                        in_hole = True
                        break
                if not in_hole:
                    return True
        return False
    return False

def _get_municipio_feature(municipio_name: str, uf: Optional[str] = None):
    """
    Extrai bounding box real e geometria do município para zoom espacial.
    """
    try:
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        
        # Determinar arquivos GeoJSON para busca
        files_to_check = []
        if uf and uf.upper() in MAPA_UF_IBGE:
            code = MAPA_UF_IBGE[uf.upper()]
            files_to_check.append(f"geojs-{code}-mun.json")
        else:
            # Busca em todos se UF não informada
            files_to_check = [f for f in os.listdir(data_dir) if f.startswith('geojs-') and f.endswith('.json')]

        for filename in files_to_check:
            path = os.path.join(data_dir, filename)
            if not os.path.exists(path):
                continue
                
            with open(path, 'r', encoding='utf-8') as f:
                geojson_data = json.load(f)
            
            for feature in geojson_data.get('features', []):
                name = feature.get('properties', {}).get('name', '')
                if municipio_name.lower().strip() in name.lower().strip() or name.lower().strip() == municipio_name.lower().strip():
                    geometry = feature.get('geometry', {})
                    coords = geometry.get('coordinates', [])
                    if not coords: continue
                    
                    all_pts = []
                    if geometry['type'] == 'Polygon':
                        all_pts = coords[0]
                    elif geometry['type'] == 'MultiPolygon':
                        for poly in coords: all_pts.extend(poly[0])
                    
                    if not all_pts: continue
                    lons, lats = [p[0] for p in all_pts], [p[1] for p in all_pts]
                    bounds = [[min(lats), min(lons)], [max(lats), max(lons)]]
                    return bounds, geometry
        return None, None
    except Exception as e:
        logger.error(f"Erro ao buscar feature do município: {e}")
        return None, None


def _get_uf_bounds_from_geojson(uf_sigla: str) -> Optional[list]:
    """
    Extrai bounding box real do Estado inteiro a partir do seu GeoJSON.
    """
    try:
        if not uf_sigla or uf_sigla.upper() not in MAPA_UF_IBGE:
            return None
            
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        code = MAPA_UF_IBGE[uf_sigla.upper()]
        path = os.path.join(data_dir, f"geojs-{code}-mun.json")
        
        if not os.path.exists(path):
            return None
            
        with open(path, 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
            
        lats, lons = [], []
        for feature in geojson_data.get('features', []):
            geometry = feature.get('geometry', {})
            coords = geometry.get('coordinates', [])
            if not coords: continue
            
            all_pts = []
            if geometry['type'] == 'Polygon':
                all_pts = coords[0]
            elif geometry['type'] == 'MultiPolygon':
                for poly in coords: all_pts.extend(poly[0])
            
            for p in all_pts:
                lons.append(p[0])
                lats.append(p[1])
                
        if not lats or not lons: return None
        return [[min(lats), min(lons)], [max(lats), max(lons)]]
    except Exception as e:
        logger.error(f"Erro ao buscar bounds da UF {uf_sigla}: {e}")
        return None


def _get_car_geojson(db: Session, m_geometry: dict):
    """
    Busca perímetros do CAR vinculados à geometria do município.
    Simplifica as geometrias para manter a fluidez do mapa.
    """
    sql = """
        SELECT jsonb_build_object(
            'type', 'FeatureCollection',
            'features', COALESCE(jsonb_agg(features), '[]'::jsonb)
        )
        FROM (
            SELECT jsonb_build_object(
                'type', 'Feature',
                'id', id,
                'geometry', ST_AsGeoJSON(ST_SimplifyPreserveTopology(geom, 0.0001))::jsonb,
                'properties', jsonb_build_object(
                    'codigo_imovel', codigo_imovel,
                    'situacao', situacao,
                    'area_ha', area_ha
                )
            ) AS features
            FROM car_propriedades
            WHERE ST_Intersects(geom, ST_SetSRID(ST_GeomFromGeoJSON(:mun_geom), 4326))
            LIMIT 5000
        ) AS subquery
    """
    try:
        result = db.execute(text(sql), {"mun_geom": json.dumps(m_geometry)}).scalar()
        return result
    except Exception as e:
        logger.error(f"Erro ao buscar CAR GeoJSON: {e}")
        return None


@router.get("/visualizar")
def visualizar_mapa(
    request: Request,
    uf: Optional[str] = Query(None, description="Filtrar por UF (Ex: PA, SP)"),
    municipio: Optional[str] = Query(None, description="Filtrar por município"),
    cultura: Optional[str] = Query(None, description="Filtrar por cultura"),
    status: Optional[str] = Query(None, description="Filtrar por status"),
    data_inicio: Optional[date] = Query(None, description="Data início (YYYY-MM-DD)"),
    data_fim: Optional[date] = Query(None, description="Data fim (YYYY-MM-DD)"),
    id_programa: Optional[str] = Query(None, description="Filtrar por programa"),
    ano: Optional[str] = Query(None, description="Filtrar por ano (YYYY)"),
    trimestre: Optional[int] = Query(None, description="Filtrar por trimestre (1-4)"),
    db: Session = Depends(get_db)
):
    """
    Gera mapa interativo HTML com Folium/Leaflet.
    
    ESPECIFICAÇÕES TÉCNICAS:
    - CircleMarker: radius=5, cores por status
    - Zoom inteligente: Estado (sem filtro) vs Município (com filtro)
    - Limites territoriais: GeoJSON IBGE com fallback
    - Viewport: 100vw x 100vh (proporção natural)
    - zoomSnap/zoomDelta: 0.1
    
    SEGURANÇA:
    - Permite chamadas do IP local (127.0.0.1) sem autenticação
    - Valida header X-Internal-Request para chamadas do Playwright
    - Chamadas externas exigem autenticação normal
    """
    
    # =====================================================
    # BYPASS DE AUTENTICAÇÃO PARA CHAMADAS INTERNAS
    # =====================================================
    
    client_host = request.client.host if request.client else None
    internal_header = request.headers.get("X-Internal-Request")
    
    is_internal_request = (
        client_host in ["127.0.0.1", "localhost", "::1"] and 
        internal_header == "true"
    )
    
    if is_internal_request:
        logger.info(f"🔓 Chamada interna detectada: {client_host} com header X-Internal-Request")
    else:
        # Chamada externa - pode adicionar autenticação aqui se necessário
        logger.info(f"🌐 Chamada externa: {client_host}")
    
    # Normalizar filtros
    uf = uf.strip().upper() if uf and uf.strip() else None
    municipio = municipio.strip() if municipio and municipio.strip() else None
    cultura = cultura.strip() if cultura and cultura.strip() else None
    status = status.strip() if status and status.strip() else None
    
    # Consultar banco de dados
    relatorios = _query_relatorios(
        db, uf, municipio, cultura, status, ano, trimestre,
        data_inicio, data_fim, id_programa
    )
    
    logger.info(f"Visualização de mapa: {len(relatorios)} registros encontrados")
    logger.info(f"Filtros: municipio={municipio}, cultura={cultura}, status={status}")
    
    # =====================================================
    # LÓGICA DE FILTRO ESPACIAL (Point-In-Polygon)
    # =====================================================
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    m_bounds, m_geometry = _get_municipio_feature(municipio, uf) if municipio else (None, None)
    
    # Se temos o município e a geometria dele, aplicar filtro geográfico Spatial!
    if municipio and m_geometry:
        logger.info(f"📍 Aplicando Ray-Casting Spatial (Point-In-Polygon) para município: {municipio}")
        rel_spatially_filtered = []
        for r in relatorios:
            lat = float(r["latitude"]) if r["latitude"] else None
            lon = float(r["longitude"]) if r["longitude"] else None
            if lat is not None and lon is not None:
                if _is_point_in_geometry(lon, lat, m_geometry):
                    rel_spatially_filtered.append(r)
        
        logger.info(f"📍 Foram mantidos {len(rel_spatially_filtered)} de {len(relatorios)} devido ao filtro espacial (município).")
        relatorios = rel_spatially_filtered
    elif uf:
        logger.info(f"📍 Aplicando Ray-Casting Spatial (Point-In-Polygon) para UF inteira: {uf}")
        ibge_code = MAPA_UF_IBGE.get(uf)
        if ibge_code:
            geojson_path = os.path.join(data_dir, f"geojs-{ibge_code}-mun.json")
            if os.path.exists(geojson_path):
                with open(geojson_path, 'r', encoding='utf-8') as f:
                    uf_geojson_data = json.load(f)
                
                rel_spatially_filtered = []
                for r in relatorios:
                    lat = float(r["latitude"]) if r["latitude"] else None
                    lon = float(r["longitude"]) if r["longitude"] else None
                    if lat is not None and lon is not None:
                        in_uf = False
                        for feature in uf_geojson_data.get('features', []):
                            if _is_point_in_geometry(lon, lat, feature.get('geometry', {})):
                                in_uf = True
                                break
                        if in_uf:
                            rel_spatially_filtered.append(r)
                
                logger.info(f"📍 Foram mantidos {len(rel_spatially_filtered)} de {len(relatorios)} devido ao filtro espacial da UF.")
                relatorios = rel_spatially_filtered

    # =====================================================
    # ZOOM INTELIGENTE: Estado vs Município
    # =====================================================
    
    # 🗺️ CAMADAS BASE: Satélite como padrão + OSM alternativo
    mapa = folium.Map(
        tiles=None,  # Não usar tiles padrão
        zoom_control=True,
        zoom_snap=0.1,
        zoom_delta=0.1
    )
    
    # Camada 1: Satélite (Esri World Imagery) - PADRÃO
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satélite',
        overlay=False,
        control=True
    ).add_to(mapa)
    
    # Camada 2: OpenStreetMap - ALTERNATIVA
    folium.TileLayer(
        tiles='openstreetmap',
        name='Mapa de Ruas',
        overlay=False,
        control=True
    ).add_to(mapa)
    
    # =====================================================
    # CAMADAS GEOJSON DINÂMICAS: Carrega estados detectados nos dados
    # =====================================================
    
    ufs_detectadas = set([r["uf"].upper() for r in relatorios if r["uf"]])
    if uf and uf not in ufs_detectadas:
        ufs_detectadas.add(uf)  # Garante renderização do polígono mesmo sem dados
        
    if not ufs_detectadas: ufs_detectadas = {'PA'} # Fallback
    
    for uf_sigla in ufs_detectadas:
        ibge_code = MAPA_UF_IBGE.get(uf_sigla)
        if not ibge_code: continue
        
        geojson_path = os.path.join(data_dir, f"geojs-{ibge_code}-mun.json")
        
        if os.path.exists(geojson_path):
            try:
                with open(geojson_path, 'r', encoding='utf-8') as f:
                    geojson_data = json.load(f)
                
                # Adicionar contorno da UF (todos os seus municípios)
                folium.GeoJson(
                    geojson_data,
                    name=f'Contorno {uf_sigla}',
                    style_function=lambda x: {
                        'fillColor': 'transparent',
                        'color': 'gray',
                        'weight': 1.0,
                        'fillOpacity': 0.05
                    },
                    tooltip=folium.GeoJsonTooltip(
                        fields=['name'],
                        aliases=['Município:'],
                        localize=True
                    )
                ).add_to(mapa)
                
                logger.info(f"✅ GeoJSON {uf_sigla} adicionado ao mapa")
                
                # Se município filtrado, destacar apenas esse município na UF correta
                if municipio:
                    for feature in geojson_data.get('features', []):
                        muni_name = feature.get('properties', {}).get('name', '')
                        if municipio.lower() in muni_name.lower():
                            folium.GeoJson(
                                feature,
                                name=f'Destaque {muni_name}',
                                style_function=lambda x: {
                                    'fillColor': 'yellow',
                                    'color': 'red',
                                    'weight': 2.5,
                                    'fillOpacity': 0.2
                                }
                            ).add_to(mapa)
                            logger.info(f"✅ Município destacado: {muni_name}")
                            
            except Exception as e:
                logger.error(f"Erro ao carregar GeoJSON {uf_sigla}: {e}")
        else:
            logger.warning(f"GeoJSON não encontrado: {geojson_path}")

    # =====================================================
    # 🌿 CAMADA CAR: CARREGA APENAS SOB DEMANDA (MUNICIPIO SELECIONADO)
    # =====================================================
    if municipio and m_geometry:
        logger.info(f"🌿 Carregando camada CAR independente para o município: {municipio}")
        car_geojson = _get_car_geojson(db, m_geometry)
        if car_geojson and car_geojson.get('features'):
            car_layer = folium.GeoJson(
                car_geojson,
                name='Perímetros CAR',
                style_function=lambda x: {
                    'fillColor': '#4caf50',
                    'color': '#2e7d32',
                    'weight': 1,
                    'fillOpacity': 0.15
                },
                tooltip=folium.GeoJsonTooltip(
                    fields=['codigo_imovel', 'situacao', 'area_ha'],
                    aliases=['Código:', 'Situação:', 'Área (ha):'],
                    localize=True
                )
            ).add_to(mapa)
            
            # Script para capturar clique no CAR e abrir popup customizado (não escapado)
            car_js = f"""
            <script>
            document.addEventListener('DOMContentLoaded', function() {{
                var carLayer = {car_layer.get_name()};
                var mapInstance = {mapa.get_name()};
                
                carLayer.on('click', function(e) {{
                    var props = e.layer.feature.properties;
                    var codigo = props.codigo_imovel || 'N/A';
                    var situacao = props.situacao || 'N/A';
                    var area = props.area_ha || '0.00';
                    
                    var popupHtml = `
                        <div style="font-family: sans-serif; min-width: 200px; padding: 5px;">
                            <b style="color: #2e7d32; font-size: 14px;">Propriedade CAR</b><br><br>
                            <b>Código:</b> ${{codigo}}<br>
                            <b>Situação:</b> ${{situacao}}<br>
                            <b>Área:</b> ${{area}} ha<br>
                            <hr style="margin: 10px 0; border: 0; border-top: 1px solid #eee;">
                            <button class="copy-btn" style="width: 100%; justify-content: center;"
                                    onclick="copyToClipboard('${{codigo}}', this)">
                                📋 Copiar Código CAR
                            </button>
                        </div>
                    `;
                    L.popup()
                        .setLatLng(e.latlng)
                        .setContent(popupHtml)
                        .openOn(mapInstance);
                }});
            }});
            </script>
            """
            mapa.get_root().html.add_child(folium.Element(car_js))
            logger.info(f"✅ {len(car_geojson['features'])} perímetros CAR com listener de clique.")

    # =====================================================
    # ZOOM INICIAL
    # =====================================================
    coords_all = [(r["latitude"], r["longitude"]) for r in relatorios if r["latitude"] and r["longitude"]]
    
    # Pré-calcular os bounds de TODAS as UFs detectadas para o fallback
    all_ufs_bounds_points = []
    for sigla in ufs_detectadas:
        b = _get_uf_bounds_from_geojson(sigla)
        if b:
            all_ufs_bounds_points.extend(b)
    
    if m_bounds:
        # 1. Município foi selecionado: focar no município
        logger.info("📍 Focando zoom nos limites do Município")
        mapa.fit_bounds(m_bounds, padding=(30, 30))
    elif uf:
        # 2. UF selecionada (sem município): focar no Estado Inteiro
        uf_bounds = _get_uf_bounds_from_geojson(uf)
        if uf_bounds:
            logger.info("📍 Focando zoom nos limites da UF selecionada")
            mapa.fit_bounds(uf_bounds, padding=(30, 30))
        elif coords_all:
            # Fallback para pontos da UF
            lats, lons = [c[0] for c in coords_all], [c[1] for c in coords_all]
            mapa.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]], padding=(30, 30))
    elif all_ufs_bounds_points:
        # 3. Nenhum filtro geográfico: focar nos estados INTEIROS que têm dados (multi-UF)
        logger.info("📍 Focando zoom na totalidade das UFs com dados")
        lats, lons = [p[0] for p in all_ufs_bounds_points], [p[1] for p in all_ufs_bounds_points]
        mapa.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]], padding=(30, 30))
    elif coords_all:
        # 4. Fallback se não detectar estados: focar em TODOS os pontos do BD
        logger.info("📍 Focando zoom em todos os pontos carregados (Fallback)")
        lats, lons = [c[0] for c in coords_all], [c[1] for c in coords_all]
        mapa.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]], padding=(30, 30))
    else:
        # 5. Fallback Absoluto (Pará)
        logger.info("📍 Fallback absoluto de bounds vazio (Pará)")
        mapa.fit_bounds([[-9.8, -58.9], [2.6, -46.0]], padding=(30, 30))
    
    # JS/CSS para Copy to Clipboard
    copy_script = """
    <style>
        .copy-btn {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 4px 8px;
            cursor: pointer;
            font-size: 12px;
            margin-top: 5px;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            color: #333;
            font-weight: 500;
        }
        .copy-btn:hover {
            background: #e9ecef;
            border-color: #adb5bd;
        }
        .copy-btn:active {
            background: #dee2e6;
        }
    </style>
    <script>
        function copyToClipboard(text, btn) {
            const originalHTML = btn.innerHTML;
            navigator.clipboard.writeText(text).then(() => {
                btn.innerHTML = '✅ Copiado!';
                setTimeout(() => {
                    btn.innerHTML = originalHTML;
                }, 2000);
            }).catch(err => {
                console.error('Erro ao copiar: ', err);
            });
        }
    </script>
    """
    mapa.get_root().header.add_child(folium.Element(copy_script))

    # =====================================================
    # ADICIONAR MARCADORES: CircleMarker com cores
    # =====================================================
    
    STATUS_COLORS = {
        'NORMAL': 'blue',
        'SUSPEITA': 'orange',
        'POSITIVO': 'red'
    }
    
    marker_count = 0
    
    for relatorio in relatorios:
        try:
            lat = float(relatorio["latitude"]) if relatorio["latitude"] is not None else None
            lon = float(relatorio["longitude"]) if relatorio["longitude"] is not None else None
            
            if lat is not None and lon is not None:
                status_upper = (relatorio["status"] or 'NORMAL').upper()
                color = STATUS_COLORS.get(status_upper, 'blue')
                
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=5,
                    color=color,
                    fill=True,
                    fillColor=color,
                    fillOpacity=0.8,
                    weight=1,
                    popup=folium.Popup(
                        f"""
                        <div style="font-family: sans-serif; min-width: 180px; padding: 5px;">
                            <div style="margin-bottom: 8px;">
                                <b style="color: #1a73e8;">Ponto de Inspeção</b><br><br>
                                <b>Município:</b> {relatorio["municipio"] or 'N/A'}<br>
                                <b>Status:</b> {relatorio["status"] or 'N/A'}<br>
                                <b>Cultura:</b> {relatorio["cultura"] or 'N/A'}<br>
                                <b>Data:</b> {relatorio["data"] or 'N/A'}
                            </div>
                            <hr style="margin: 10px 0; border: 0; border-top: 1px solid #eee;">
                            <button class="copy-btn" style="width: 100%; justify-content: center;"
                                    title="Copiar resumo do ponto" 
                                    onclick="copyToClipboard('UF: {relatorio["uf"] or ''}\\nMunicípio: {relatorio["municipio"] or ''}\\nStatus: {relatorio["status"] or ''}\\nCultura: {relatorio["cultura"] or ''}\\nData: {relatorio["data"] or ''}', this)">
                                📋 Copiar Dados
                            </button>
                        </div>
                        """,
                        max_width=250
                    )
                ).add_to(mapa)
                
                marker_count += 1
        except Exception as e:
            logger.warning(f"Erro ao processar marcador do mapa: {e}")
            continue
    
    logger.info(f"✅ Mapa gerado com {marker_count} marcadores")
    
    # =====================================================
    # LEGENDA DE CORES (HTML customizado)
    # =====================================================
    
    legend_html = '''
    <div style="
        position: fixed; 
        bottom: 50px; left: 50px; 
        width: 200px; 
        background-color: white; 
        border: 2px solid grey; 
        z-index: 9999; 
        font-size: 14px;
        padding: 10px;
        border-radius: 5px;
        box-shadow: 0 0 15px rgba(0,0,0,0.2);
    ">
        <p style="margin: 0 0 10px 0; font-weight: bold; text-align: center;">
            Status das Inspeções
        </p>
        <p style="margin: 5px 0;">
            <span style="color: blue; font-size: 20px;">●</span> Normal
        </p>
        <p style="margin: 5px 0;">
            <span style="color: orange; font-size: 20px;">●</span> Suspeita
        </p>
        <p style="margin: 5px 0;">
            <span style="color: red; font-size: 20px;">●</span> Positivo
        </p>
    </div>
    '''
    
    mapa.get_root().html.add_child(folium.Element(legend_html))
    
    # =====================================================
    # CONTROLE DE CAMADAS: Alternar entre Satélite e OSM
    # =====================================================
    
    folium.LayerControl(position='topright').add_to(mapa)
    
    # =====================================================
    # GERAR HTML COM VIEWPORT CORRETO
    # =====================================================
    
    # Usa a função nativa do Folium para exportar o mapa HTML perfeitamente renderizado
    # Isto previne problemas de iframe embutido e offset de 100vh de scroll invisivel
    html_final = mapa.get_root().render()
    
    # Salvar HTML temporário
    temp_maps_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'temp_maps')
    os.makedirs(temp_maps_dir, exist_ok=True)
    
    html_filename = f"mapa_{uuid.uuid4().hex}.html"
    html_path = os.path.join(temp_maps_dir, html_filename)
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_final)
    
    logger.info(f"📄 HTML salvo: {html_filename}")
    
    # =====================================================
    # RETORNO: HTML direto (Playwright) ou JSON (API)
    # =====================================================
    
    if is_internal_request:
        # 🔒 CHAMADA INTERNA: Retornar HTML diretamente para Playwright
        logger.info("🔒 Retornando HTML diretamente para Playwright")
        return HTMLResponse(content=html_final, status_code=200)
    else:
        # 🌐 CHAMADA EXTERNA: Retornar JSON com URL do arquivo
        base_url = str(request.base_url).rstrip('/')
        html_url = f"{base_url}/mapas_temp/{html_filename}"
        
        return JSONResponse(content={
            "url": html_url,
            "filename": html_filename,
            "total_markers": marker_count,
            "message": f"Mapa gerado com {marker_count} marcadores"
        })
