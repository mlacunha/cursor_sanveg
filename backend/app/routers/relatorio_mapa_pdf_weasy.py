"""
Nova rota para geração de PDF de mapas usando WeasyPrint.
Compatível com hospedagem compartilhada (Integrator ICP).
Rota independente que não afeta o mapa HTML existente.
"""

from fastapi import APIRouter, Depends, Query, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from typing import Optional
from datetime import date
import folium
import logging
import json
import os
import uuid

from app.config.database import get_db
from app.utils.security import get_current_user
from app.models.users import User
from app.models.relatorio_mapa import RelatorioMapa
from app.models.municipio import Municipio

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/relatorio-mapa-pdf",
    tags=["relatorio-mapa-pdf"]
)


def _query_relatorios(db: Session,
                      municipio: Optional[str],
                      cultura: Optional[str],
                      status: Optional[str],
                      data_inicio: Optional[date],
                      data_fim: Optional[date],
                      id_programa: Optional[str],
                      ano: Optional[str],
                      trimestre: Optional[int]):
    """Build and execute the RelatorioMapa query using the same filters as the endpoints."""
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


def _build_map_html_for_pdf(relatorios, title: Optional[str] = None):
    """
    Create folium HTML optimized for PDF generation.
    Returns (map_html, marker_count).
    """
    # Resolve coordinates
    valid_records = []
    for r in relatorios:
        resolved_lat = None
        resolved_lon = None

        if r.latitude is not None and r.longitude is not None:
            try:
                resolved_lat = float(r.latitude)
                resolved_lon = float(r.longitude)
            except (TypeError, ValueError):
                resolved_lat = None
                resolved_lon = None

        if (resolved_lat is None or resolved_lon is None) and getattr(r, 'propriedade_data', None):
            prop = r.propriedade_data
            if prop and prop.latitude is not None and prop.longitude is not None:
                try:
                    resolved_lat = float(prop.latitude)
                    resolved_lon = float(prop.longitude)
                except (TypeError, ValueError):
                    resolved_lat = None
                    resolved_lon = None

        if resolved_lat is not None and resolved_lon is not None:
            valid_records.append({
                'relatorio': r,
                'lat': resolved_lat,
                'lon': resolved_lon
            })

    if not valid_records:
        logger.warning("No valid coordinates found for map generation")
        # Create empty map centered on Brazil
        m = folium.Map(location=[-14.235, -51.925], zoom_start=4)
        return m.get_root().render(), 0

    # Calculate map center
    avg_lat = sum(rec['lat'] for rec in valid_records) / len(valid_records)
    avg_lon = sum(rec['lon'] for rec in valid_records) / len(valid_records)

    # Create map with single layer (simpler for PDF)
    m = folium.Map(
        location=[avg_lat, avg_lon],
        zoom_start=6,
        tiles='OpenStreetMap'
    )

    # Status colors
    status_colors = {
        'NORMAL': 'green',
        'SUSPEITA': 'orange',
        'POSITIVO': 'red',
        'FOCO': 'red'
    }

    # Add markers
    for rec in valid_records:
        r = rec['relatorio']
        lat = rec['lat']
        lon = rec['lon']

        color = status_colors.get(r.status.upper() if r.status else 'NORMAL', 'blue')

        # Format date properly
        data_formatada = 'N/A'
        if r.data:
            if hasattr(r.data, 'strftime'):
                data_formatada = r.data.strftime('%d/%m/%Y')
            else:
                data_formatada = str(r.data)
        
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; font-size: 12px; width: 250px;">
            <h4 style="margin: 0 0 10px 0; color: #333;">Inspeção Agropecuária</h4>
            <p style="margin: 5px 0;"><strong>Município:</strong> {r.municipio or 'N/A'}</p>
            <p style="margin: 5px 0;"><strong>Cultura:</strong> {r.cultura or 'N/A'}</p>
            <p style="margin: 5px 0;"><strong>Status:</strong> {r.status or 'N/A'}</p>
            <p style="margin: 5px 0;"><strong>Data:</strong> {data_formatada}</p>
            <p style="margin: 5px 0;"><strong>Programa:</strong> {r.programa_data.nome if r.programa_data else 'N/A'}</p>
        </div>
        """

        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color=color, icon='info-sign')
        ).add_to(m)

    # 🗺️ ENQUADRAMENTO: Forçar visualização do Estado do Pará
    # Coordenadas: Sudoeste [-9.8, -58.9] até Nordeste [2.6, -46.0]
    para_bounds = [[-9.8, -58.9], [2.6, -46.0]]
    m.fit_bounds(para_bounds)

    # Add title if provided
    if title:
        title_html = f'''
        <div style="position: fixed; 
                    top: 10px; 
                    left: 50%; 
                    transform: translateX(-50%);
                    background-color: white; 
                    padding: 10px 20px; 
                    border: 2px solid #333;
                    border-radius: 5px;
                    z-index: 9999;
                    font-family: Arial, sans-serif;
                    font-size: 16px;
                    font-weight: bold;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.3);">
            {title}
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

    return m.get_root().render(), len(valid_records)


@router.get("/gerar")
def gerar_mapa_pdf(
    request: Request,
    municipio: Optional[str] = Query(None, description="Filtrar por município"),
    cultura: Optional[str] = Query(None, description="Filtrar por cultura"),
    status: Optional[str] = Query(None, description="Filtrar por status"),
    data_inicio: Optional[date] = Query(None, description="Data início (YYYY-MM-DD)"),
    data_fim: Optional[date] = Query(None, description="Data fim (YYYY-MM-DD)"),
    id_programa: Optional[str] = Query(None, description="Filtrar por programa"),
    ano: Optional[str] = Query(None, description="Filtrar por ano (YYYY)"),
    trimestre: Optional[int] = Query(None, description="Filtrar por trimestre (1-4)"),
    title: Optional[str] = Query("Mapa de Inspeções Agropecuárias", description="Título do PDF"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    NOVA ROTA: Gera PDF do mapa usando xhtml2pdf (compatível com Windows e hospedagem compartilhada).
    
    Esta rota é independente e não afeta o mapa HTML existente.
    Funciona no Windows local e no painel Integrator ICP sem dependências externas.
    
    Retorna:
        JSON com URL do PDF gerado para abertura em página ou iframe.
    """
    
    # Normalize inputs
    municipio = municipio if municipio and municipio.strip() else None
    cultura = cultura if cultura and cultura.strip() else None
    status = status if status and status.strip() else None
    id_programa = id_programa if id_programa and id_programa.strip() else None
    ano = ano if ano and ano.strip() else None

    logger.info(
        "Generating PDF map with filters: municipio=%s, cultura=%s, status=%s, ano=%s, trimestre=%s",
        municipio, cultura, status, ano, trimestre
    )

    # Query relatorios
    relatorios = _query_relatorios(db, municipio, cultura, status, data_inicio, data_fim, id_programa, ano, trimestre)
    
    logger.info("Found %d records for PDF map", len(relatorios))

    # Build HTML map
    map_html, marker_count = _build_map_html_for_pdf(relatorios, title=title)

    # Prepare temp directory
    temp_maps_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "temp_maps"
    )
    os.makedirs(temp_maps_dir, exist_ok=True)

    # Save HTML temporarily
    html_filename = f"mapa_temp_{uuid.uuid4().hex}.html"
    html_path = os.path.join(temp_maps_dir, html_filename)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(map_html)

    # Generate PDF filename
    pdf_filename = f"mapa_pdf_{uuid.uuid4().hex}.pdf"
    pdf_path = os.path.join(temp_maps_dir, pdf_filename)

    # Convert HTML to PDF using xhtml2pdf
    try:
        from xhtml2pdf import pisa
    except ImportError:
        raise HTTPException(
            status_code=500, 
            detail="xhtml2pdf não está instalado. Adicione 'xhtml2pdf' ao requirements.txt"
        )

    try:
        logger.info("Converting HTML to PDF using xhtml2pdf...")
        
        # Read HTML content
        with open(html_path, 'r', encoding='utf-8') as html_file:
            source_html = html_file.read()
        
        # Create PDF
        with open(pdf_path, 'wb') as pdf_file:
            pisa_status = pisa.CreatePDF(source_html, dest=pdf_file)
        
        if pisa_status.err:
            raise Exception(f"Erro ao converter HTML para PDF: {pisa_status.err}")
        
        logger.info("PDF generated successfully: %s", pdf_filename)
        
        # Clean up temporary HTML
        try:
            os.remove(html_path)
        except:
            pass
            
    except Exception as e:
        logger.error(f"Error generating PDF with xhtml2pdf: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao gerar PDF: {str(e)}"
        )

    # Build PDF URL
    base_url = str(request.base_url).rstrip('/')
    pdf_url = f"{base_url}/mapas_temp/{pdf_filename}"

    logger.info(
        "PDF map generated successfully with %d markers, saved to %s",
        marker_count, pdf_filename
    )

    return JSONResponse(content={
        "url": pdf_url,
        "filename": pdf_filename,
        "markers": marker_count,
        "message": "PDF gerado com sucesso"
    }, status_code=200)
