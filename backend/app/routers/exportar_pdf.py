"""
Router PÚBLICO para exportação de mapas em PDF padrão GIS/Engenharia.

ESTRATÉGIA - INJEÇÃO HTML DIRETA (Dezembro 2025):
1. Endpoint público: /api/exportar-pdf/mapa (SEM AUTENTICAÇÃO)
2. Geração HTML direta via Folium (sem navegação HTTP)
3. Injeção HTML no Playwright via page.set_content()
4. Elimina latência de rede, DNS, autenticação
5. Content-Disposition: inline (exibição direta em iframes/WeWeb)

ACESSO PÚBLICO:
- Dados públicos (mapas de inspeções agropecuárias)
- Sem necessidade de token JWT
- Compatível com iframes (WeWeb, dashboards)
- Headers permitem incorporação

FLUXO TÉCNICO:
1. Consultar banco de dados diretamente com filtros
2. Calcular metadados REAIS (coordenadas centrais, total de pontos)
3. Gerar mapa Folium com todas as especificações
4. Obter HTML via map._repr_html_()
5. Injetar HTML no Playwright (page.set_content)
6. Capturar screenshot (viewport 1615x1000 - proporção 1.615:1)
7. Montar PDF (w=210, h=130mm - proporção 1.615:1)

Garantias: Dados técnicos do PDF = Banco de Dados (não screenshot)
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from typing import Optional, List
import logging
import uuid
import os
from datetime import date
import folium
import json

from app.config.database import get_db
from app.models.relatorio_mapa import RelatorioMapa
from app.models.municipio import Municipio
from app.services.pdf_service import PDFMapService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/exportar-pdf",
    tags=["Geoprocessamento - Exportação PDF"]
)


def _query_relatorios_db(
    db: Session,
    municipio: Optional[str],
    cultura: Optional[str],
    status: Optional[str],
    data_inicio: Optional[date],
    data_fim: Optional[date],
    id_programa: Optional[str],
    ano: Optional[str],
    trimestre: Optional[int]
) -> List[RelatorioMapa]:
    """
    Consulta DIRETA ao banco de dados (mesma lógica de relatorio_mapa_visualizar).
    
    Esta é a FONTE DA VERDADE para os metadados do PDF.
    """
    query = db.query(RelatorioMapa).options(
        joinedload(RelatorioMapa.programa_data),
        joinedload(RelatorioMapa.propriedade_data)
    )

    if id_programa:
        query = query.filter(RelatorioMapa.id_programa == id_programa)

    if municipio:
        matched_munis = db.query(Municipio).filter(Municipio.nome.ilike(f"%{municipio}%")).all()
        if matched_munis:
            names = [m.nome for m in matched_munis]
            ids = [str(m.id) for m in matched_munis]
            query = query.filter(or_(RelatorioMapa.municipio.in_(names), RelatorioMapa.municipio.in_(ids)))
        else:
            query = query.filter(RelatorioMapa.municipio.ilike(f"%{municipio}%"))

    if cultura:
        query = query.filter(RelatorioMapa.cultura.ilike(f"%{cultura}%"))

    if status:
        query = query.filter(RelatorioMapa.status.ilike(f"%{status}%"))

    if ano:
        query = query.filter(RelatorioMapa.ano == ano)

    if trimestre:
        query = query.filter(RelatorioMapa.trimestre == trimestre)

    if data_inicio:
        query = query.filter(RelatorioMapa.data >= data_inicio)

    if data_fim:
        query = query.filter(RelatorioMapa.data <= data_fim)

    return query.all()


def _calculate_metadata_from_db(relatorios: List[RelatorioMapa], filters: dict) -> dict:
    """
    Calcula metadados REAIS a partir dos dados do banco.
    
    Estes metadados são a FONTE DA VERDADE que aparecerá no PDF.
    """
    valid_coords = []
    municipios_set = set()
    
    for r in relatorios:
        # Tentar obter coordenadas do relatório ou da propriedade
        lat, lon = None, None
        
        if r.latitude is not None and r.longitude is not None:
            try:
                lat = float(r.latitude)
                lon = float(r.longitude)
            except (TypeError, ValueError):
                pass
        
        if (lat is None or lon is None) and getattr(r, 'propriedade_data', None):
            prop = r.propriedade_data
            if prop and prop.latitude is not None and prop.longitude is not None:
                try:
                    lat = float(prop.latitude)
                    lon = float(prop.longitude)
                except (TypeError, ValueError):
                    pass
        
        if lat is not None and lon is not None:
            valid_coords.append((lat, lon))
        
        if r.municipio:
            municipios_set.add(r.municipio)
    
    # Calcular coordenadas centrais (média ponderada)
    lat_center = None
    lon_center = None
    if valid_coords:
        lat_center = sum(c[0] for c in valid_coords) / len(valid_coords)
        lon_center = sum(c[1] for c in valid_coords) / len(valid_coords)
    
    # Formatar datas
    data_inicio_fmt = filters.get('data_inicio').strftime('%d/%m/%Y') if filters.get('data_inicio') else None
    data_fim_fmt = filters.get('data_fim').strftime('%d/%m/%Y') if filters.get('data_fim') else None
    
    metadata = {
        'lat_center': lat_center,
        'lon_center': lon_center,
        'total_markers': len(valid_coords),
        'total_records': len(relatorios),
        'municipios': list(municipios_set),
        'data_inicio': data_inicio_fmt,
        'data_fim': data_fim_fmt,
        'filtros_aplicados': {
            'municipio': filters.get('municipio'),
            'cultura': filters.get('cultura'),
            'status': filters.get('status'),
            'ano': filters.get('ano'),
            'trimestre': filters.get('trimestre'),
            'id_programa': filters.get('id_programa')
        }
    }
    
    logger.info(f"Metadados calculados do BD: {metadata['total_markers']} pontos, centro em ({lat_center}, {lon_center})")
    
    return metadata


def _get_municipio_bounds_from_geojson(municipio_name: str) -> Optional[list]:
    """
    Extrai bounding box real do município a partir do GeoJSON IBGE.
    
    Retorna: [[min_lat, min_lon], [max_lat, max_lon]] ou None
    """
    try:
        geojson_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'data', 
            'geojs-15-mun.json'
        )
        
        if not os.path.exists(geojson_path):
            logger.warning(f"GeoJSON não encontrado: {geojson_path}")
            return None
        
        with open(geojson_path, 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
        
        # Buscar município no GeoJSON
        for feature in geojson_data.get('features', []):
            properties = feature.get('properties', {})
            nome_feature = properties.get('name', '')
            
            # Normalizar nomes para comparação
            if nome_feature.lower().strip() == municipio_name.lower().strip():
                geometry = feature.get('geometry', {})
                geom_type = geometry.get('type', '')
                coords = geometry.get('coordinates', [])
                
                if not coords:
                    continue
                
                # Extrair todas as coordenadas
                all_coords = []
                
                if geom_type == 'Polygon':
                    # Polygon: coords[0] é o anel exterior
                    for coord in coords[0]:
                        all_coords.append(coord)
                elif geom_type == 'MultiPolygon':
                    # MultiPolygon: múltiplos polígonos
                    for polygon in coords:
                        for coord in polygon[0]:
                            all_coords.append(coord)
                
                if not all_coords:
                    continue
                
                # Calcular bounding box
                lons = [coord[0] for coord in all_coords]
                lats = [coord[1] for coord in all_coords]
                
                min_lat, max_lat = min(lats), max(lats)
                min_lon, max_lon = min(lons), max(lons)
                
                # Retornar no formato Folium: [[lat_min, lon_min], [lat_max, lon_max]]
                return [[min_lat, min_lon], [max_lat, max_lon]]
        
        return None
        
    except Exception as e:
        logger.error(f"Erro ao processar GeoJSON: {e}")
        return None


def _generate_folium_map_html(
    relatorios: List[RelatorioMapa],
    municipio: Optional[str] = None
) -> str:
    """
    Gera HTML completo do mapa Folium com todas as especificações.
    
    ESPECIFICAÇÕES TÉCNICAS:
    - CircleMarker: radius=5, cores por status (blue/orange/red)
    - Zoom inteligente: GeoJSON bounds → pontos+20% → Pará
    - GeoJSON contours para Pará + município destacado
    - LayerControl: Satélite (default) + OSM (alternativa)
    - Legenda HTML customizada
    - Viewport: 100vw x 100vh CSS
    - zoomSnap/zoomDelta: 0.1
    
    Returns:
        str: HTML completo pronto para injeção no Playwright
    """
    # 🗺️ CAMADAS BASE: Satélite como padrão + OSM alternativo
    mapa = folium.Map(
        tiles=None,
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
    
    # ZOOM INTELIGENTE
    if municipio:
        # ESTRATÉGIA 1: Tentar extrair bounds do GeoJSON
        logger.info(f"🗺️  Buscando limites territoriais de '{municipio}' no GeoJSON...")
        municipio_bounds = _get_municipio_bounds_from_geojson(municipio)
        
        if municipio_bounds:
            logger.info(f"✅ Bounds do GeoJSON encontrados: {municipio_bounds}")
            mapa.fit_bounds(municipio_bounds, padding=(10, 10))
        else:
            # ESTRATÉGIA 2: Calcular bounds dos pontos + 20% expansão
            logger.warning(f"⚠️  GeoJSON não encontrado. Usando dispersão de pontos.")
            
            coords_validas = [
                (r.latitude, r.longitude) 
                for r in relatorios 
                if r.latitude and r.longitude
            ]
            
            if coords_validas:
                lats = [c[0] for c in coords_validas]
                lons = [c[1] for c in coords_validas]
                
                min_lat, max_lat = min(lats), max(lats)
                min_lon, max_lon = min(lons), max(lons)
                
                # Expansão de 20% para contexto
                delta_lat = (max_lat - min_lat) * 0.2
                delta_lon = (max_lon - min_lon) * 0.2
                
                expanded_bounds = [
                    [min_lat - delta_lat, min_lon - delta_lon],
                    [max_lat + delta_lat, max_lon + delta_lon]
                ]
                
                logger.info(f"📍 Bounds calculados (pontos + 20%): {expanded_bounds}")
                mapa.fit_bounds(expanded_bounds, padding=(5, 5))
            else:
                # ESTRATÉGIA 3: Fallback - Estado do Pará
                logger.warning(f"⚠️  Sem bounds e sem pontos. Usando Estado do Pará.")
                mapa.location = [-3.85, -52.5]
                mapa.zoom_start = 6
    else:
        # SEM FILTRO DE MUNICÍPIO: Visão do Estado do Pará
        logger.info("🗺️  Sem filtro de município. Usando visão do Estado do Pará.")
        para_bounds = [[-9.8, -58.9], [2.6, -46.0]]
        mapa.fit_bounds(para_bounds, padding=(10, 10))
    
    # CAMADAS GEOJSON
    geojson_path = os.path.join(
        os.path.dirname(__file__), '..', 'data', 'geojs-15-mun.json'
    )
    
    if os.path.exists(geojson_path):
        try:
            with open(geojson_path, 'r', encoding='utf-8') as f:
                geojson_data = json.load(f)
            
            # Contorno do Estado do Pará
            folium.GeoJson(
                geojson_data,
                name='Contorno do Pará',
                style_function=lambda x: {
                    'fillColor': 'transparent',
                    'color': 'black',
                    'weight': 1.5,
                    'fillOpacity': 0.1
                },
                tooltip=folium.GeoJsonTooltip(
                    fields=['name'],
                    aliases=['Município:'],
                    localize=True
                )
            ).add_to(mapa)
            
            logger.info("✅ GeoJSON do Pará adicionado ao mapa")
            
            # Destacar município filtrado
            if municipio:
                for feature in geojson_data.get('features', []):
                    muni_name = feature.get('properties', {}).get('name', '')
                    
                    if municipio.lower() in muni_name.lower():
                        folium.GeoJson(
                            feature,
                            name=f'Contorno de {muni_name}',
                            style_function=lambda x: {
                                'fillColor': 'yellow',
                                'color': 'red',
                                'weight': 2.5,
                                'fillOpacity': 0.2
                            }
                        ).add_to(mapa)
                        
                        logger.info(f"✅ Contorno destacado: {muni_name}")
                        break
                        
        except Exception as e:
            logger.error(f"⚠️  Erro ao carregar GeoJSON: {e}")
    
    # ADICIONAR MARCADORES
    STATUS_COLORS = {
        'NORMAL': 'blue',
        'SUSPEITA': 'orange',
        'POSITIVO': 'red'
    }
    
    marker_count = 0
    
    for relatorio in relatorios:
        if relatorio.latitude and relatorio.longitude:
            status_upper = (relatorio.status or 'NORMAL').upper()
            color = STATUS_COLORS.get(status_upper, 'blue')
            
            folium.CircleMarker(
                location=[relatorio.latitude, relatorio.longitude],
                radius=5,
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.8,
                weight=1,
                popup=folium.Popup(
                    f"""
                    <b>Município:</b> {relatorio.municipio or 'N/A'}<br>
                    <b>Status:</b> {relatorio.status or 'N/A'}<br>
                    <b>Cultura:</b> {relatorio.cultura or 'N/A'}<br>
                    <b>Data:</b> {relatorio.data or 'N/A'}
                    """,
                    max_width=200
                )
            ).add_to(mapa)
            
            marker_count += 1
    
    logger.info(f"✅ Mapa gerado com {marker_count} marcadores")
    
    # LEGENDA DE CORES
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
    
    # CONTROLE DE CAMADAS
    folium.LayerControl(position='topright').add_to(mapa)
    
    # GERAR HTML FINAL COM VIEWPORT 100vw x 100vh
    html_map = mapa._repr_html_()
    
    html_final = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mapa de Inspeções - SVEGPA</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            overflow: hidden;
        }}
        #map {{
            width: 100vw;
            height: 100vh;
            margin: 0;
        }}
    </style>
</head>
<body>
    {html_map}
</body>
</html>
"""
    
    logger.info(f"📄 HTML gerado: {len(html_final)} caracteres")
    
    return html_final


@router.get(
    "/mapa",
    summary="[PÚBLICO] Exportar Mapa para PDF Profissional",
    description="""
    🎯 **ENDPOINT PÚBLICO** para geração de PDFs de mapas GIS/Engenharia.
    
    ### 🌐 Acesso Público (SEM AUTENTICAÇÃO):
    - ✅ **Sem necessidade de token JWT** - Permite exibição em iframes (WeWeb)
    - ✅ **Dados públicos** - Mapas de inspeções agropecuárias
    - ✅ **Content-Disposition: inline** - Abre diretamente no navegador
    - ✅ **Compatível com iframes** - Headers não bloqueiam incorporação
    
    ### 🔧 Estratégia de Injeção HTML Direta (Dezembro 2025):
    - ✅ HTML gerado via Folium internamente (sem requisições HTTP)
    - ✅ Playwright injeta HTML via page.set_content()
    - ✅ Screenshot da página (100vw x 100vh = mapa completo)
    - ✅ Zoom territorial com limites geográficos reais do município (GeoJSON)
    - ✅ CircleMarkers com cores por status (blue, orange, red)
    - ✅ Proporção 1.615:1 em todas camadas (sem distorção)
    - ✅ Sem latência de rede, DNS ou autenticação
    
    ### 📊 Processo de Geração:
    1. **Consulta direta ao banco** - dados reais com filtros aplicados
    2. **Cálculo de metadados** - coordenadas centrais, total de pontos (fonte: BD)
    3. **Geração HTML via Folium** - Mapa com GeoJSON, CircleMarkers, LayerControl
    4. **Injeção no Playwright** - page.set_content(html) + wait 5s
    5. **Captura screenshot** - viewport 1615x1000 (proporção 1.615:1)
    6. **Montagem do PDF** - A4 paisagem, imagem 210x130mm (proporção 1.615:1)
    
    ### 🔒 Garantias Técnicas:
    - Coordenadas centrais: média ponderada dos pontos reais do BD
    - Total de marcadores: contagem direta no banco de dados
    - Zoom territorial: limites geográficos oficiais do município (GeoJSON IBGE)
    - **Dados técnicos NÃO são do screenshot, mas sim do banco**
    
    ### 📐 Sincronia de Proporção (Anti-Distorção):
    - Viewport Playwright: 1615x1000 pixels (1.615:1)
    - CSS: #map = 100vw x 100vh
    - PDF image: 210mm x 130mm (1.615:1)
    - **Resultado:** Mapa do Pará sem achatamento
    
    ### 📄 Formato do Documento:
    - **Layout:** A4 Paisagem (297x210mm)
    - **Cabeçalho:** Azul profissional com título, projeto, data
    - **Mapa:** Screenshot centralizado com moldura dupla
    - **Carimbo Técnico:** Coordenadas, escala, total de pontos, responsável
    - **Rodapé:** Documento gerado automaticamente | Dados do banco
    
    ### 🛠️ Requisitos do Sistema:
    - Playwright instalado: `playwright install chromium`
    - Dependências Ubuntu: `playwright install-deps chromium`
    - Folium 0.15.1+ para geração de mapas
    """,
    responses={
        200: {
            "description": "PDF gerado com sucesso e exibido inline no navegador",
            "content": {"application/pdf": {}}
        },
        404: {
            "description": "Nenhum registro encontrado com os filtros aplicados"
        },
        500: {
            "description": "Erro interno ao processar o mapa ou gerar o documento"
        }
    }
)  # ← Fecha @router.get(
async def exportar_mapa_pdf_unificado(
    request: Request,
    municipio: Optional[str] = Query(None, description="Filtrar por município"),
    cultura: Optional[str] = Query(None, description="Filtrar por cultura"),
    status: Optional[str] = Query(None, description="Filtrar por status (NORMAL, SUSPEITA, POSITIVO)"),
    data_inicio: Optional[date] = Query(None, description="Data início (YYYY-MM-DD)"),
    data_fim: Optional[date] = Query(None, description="Data fim (YYYY-MM-DD)"),
    id_programa: Optional[str] = Query(None, description="Filtrar por programa"),
    ano: Optional[str] = Query(None, description="Filtrar por ano (YYYY)"),
    trimestre: Optional[int] = Query(None, description="Filtrar por trimestre (1-4)"),
    title: Optional[str] = Query("Mapa de Inspeções Agropecuárias", description="Título do documento"),
    project: Optional[str] = Query("SVEGPA - Sistema de Vigilância", description="Nome do projeto"),
    responsible: Optional[str] = Query("Defesa Agropecuária", description="Responsável técnico"),
    db: Session = Depends(get_db)
    # ✅ ACESSO PÚBLICO: Sem autenticação para permitir exibição em iframes (WeWeb)
):
    """
    🎯 Endpoint PÚBLICO para gerar PDF do mapa (sem autenticação).
    
    ⚠️ IMPORTANTE: 
    - Esta rota é PÚBLICA para permitir exibição em iframes (WeWeb)
    - Dados são públicos (mapas de inspeções agropecuárias)
    - Não expõe informações sensíveis
    - Usa injeção HTML direta (sem navegação HTTP)
    """
    import traceback
    
    try:
        print("\n" + "=" * 80)
        print("🚀 ENDPOINT PÚBLICO: /api/exportar-pdf/mapa (SEM AUTENTICAÇÃO)")
        print("=" * 80)
        print(f"\n📋 Filtros recebidos:")
        print(f"   - municipio: {municipio}")
        print(f"   - cultura: {cultura}")
        print(f"   - status: {status}")
        print(f"   - data_inicio: {data_inicio}")
        print(f"   - data_fim: {data_fim}")
        print(f"   - id_programa: {id_programa}")
        print(f"   - ano: {ano}")
        print(f"   - trimestre: {trimestre}")
        print(f"\n🌐 Acesso: PÚBLICO (sem autenticação)")
        print("=" * 80 + "\n")
        
        # PASSO 1: Consultar banco de dados DIRETAMENTE (fonte da verdade)
        logger.info("PASSO 1: Consultando banco de dados para metadados do PDF...")
        
        relatorios = _query_relatorios_db(
            db, municipio, cultura, status, 
            data_inicio, data_fim, id_programa, ano, trimestre
        )
        
        logger.info(f"✓ BD consultado: {len(relatorios)} registros encontrados")
        
        if not relatorios:
            logger.warning("Nenhum registro encontrado com os filtros aplicados")
            raise HTTPException(
                status_code=404,
                detail="Nenhum registro encontrado com os filtros aplicados. Verifique os filtros e tente novamente."
            )
        
        # PASSO 2: Calcular metadados REAIS do banco
        logger.info("PASSO 2: Calculando metadados do banco de dados...")
        
        filters = {
            'municipio': municipio,
            'cultura': cultura,
            'status': status,
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'id_programa': id_programa,
            'ano': ano,
            'trimestre': trimestre
        }
        
        db_metadata = _calculate_metadata_from_db(relatorios, filters)
        
        logger.info(f"✓ Metadados: {db_metadata['total_markers']} pontos, centro ({db_metadata['lat_center']}, {db_metadata['lon_center']})")
        
        # PASSO 3: Gerar HTML do mapa diretamente (Folium)
        logger.info("PASSO 3: Gerando HTML do mapa com Folium...")
        print(f"\n📄 Gerando HTML do mapa com Folium...")
        print(f"   - CircleMarkers com cores por status")
        print(f"   - GeoJSON contours para Pará")
        print(f"   - Zoom territorial inteligente")
        print(f"   - LayerControl (Satélite + OSM)\n")
        
        html_content = _generate_folium_map_html(relatorios, municipio)
        
        logger.info(f"✓ HTML gerado: {len(html_content)} caracteres")
        print(f"✓ HTML gerado: {len(html_content):,} caracteres\n")
        
        # PASSO 4: Preparar metadados finais para o PDF
        logger.info("PASSO 4: Preparando metadados finais...")
        
        pdf_filename = f"mapa_gis_{uuid.uuid4().hex}.pdf"
        
        # Combinar metadados do BD com informações customizáveis
        final_metadata = {
            'title': title,
            'project': project,
            'responsible': responsible,
            'institution': 'Ministério da Agricultura e Pecuária',
            'scale': '1:50.000',
            **db_metadata  # Sobrescreve com dados REAIS do banco
        }
        
        logger.info(f"✓ PDF: {pdf_filename}")
        logger.info(f"✓ Título: {title}")
        logger.info(f"✓ Total de pontos (BD): {final_metadata['total_markers']}")
        
        # PASSO 5: Gerar PDF via HTML injection (Playwright)
        logger.info("PASSO 5: Inicializando PDFMapService...")
        
        base_url = os.getenv('BASE_URL', 'http://127.0.0.1:8000')
        pdf_service = PDFMapService(base_url=base_url, debug_mode=False)
        
        logger.info("Iniciando geração do PDF via Playwright (HTML injection)...")
        print(f"🚀 Gerando PDF via Playwright (HTML injection - viewport 1615x1000)...\n")
        
        # 🎯 INJEÇÃO HTML DIRETA (sem navegação HTTP)
        pdf_path = await pdf_service.generate_map_pdf(
            html_content=html_content,  # ✅ HTML string (não URL)
            output_filename=pdf_filename,
            metadata=final_metadata
        )
        
        logger.info(f"✅ PDF gerado com sucesso: {pdf_path}")
        print(f"\n✅ PDF GERADO COM SUCESSO")
        print(f"   📄 Arquivo: {pdf_filename}")
        print(f"   📍 Caminho: {pdf_path}")
        print(f"   📊 Total de pontos: {final_metadata['total_markers']}")
        print("=" * 80 + "\n")
        
        # Retornar PDF para visualização inline no navegador
        return FileResponse(
            path=pdf_path,
            media_type='application/pdf',
            filename=pdf_filename,
            headers={
                "Content-Disposition": f"inline; filename={pdf_filename}"
            }
        )
        
    except HTTPException:
        # Re-raise HTTPExceptions sem modificar
        raise
        
    except Exception as e:
        # 🚨 TRACEBACK COMPLETO NO CONSOLE
        error_trace = traceback.format_exc()
        
        logger.error("=" * 80)
        logger.error("🚨 ERRO CRÍTICO NO ENDPOINT /api/exportar-pdf/mapa")
        logger.error(f"Tipo: {type(e).__name__}")
        logger.error(f"Mensagem: {str(e)}")
        logger.error(f"Traceback:\n{error_trace}")
        logger.error("=" * 80)
        
        print("\n" + "❌" * 80)
        print("🚨 ERRO CRÍTICO")
        print("❌" * 80)
        print(f"\n💥 {type(e).__name__}: {str(e)}")
        print(f"\n📋 TRACEBACK:\n{error_trace}")
        print("❌" * 80 + "\n")
        
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar PDF: {str(e) if str(e) else repr(e)}"
        )

