from fastapi import (
    APIRouter, Depends, HTTPException, status, UploadFile, File
)
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text
from typing import List, Optional
from decimal import Decimal
import csv
import io

from app.config.database import get_db
from app.models.relatorio_mapa import RelatorioMapa
from app.models.programa import Programa
from app.models.orgao import Orgao
from app.models.users import User
from app.models.propriedade import Propriedade
from app.models.termo_inspecao import TermoInspecao
from app.models.municipio import Municipio
from app.models.estado import Estado
from app.services.locations import attach_location_info, attach_location_info_batch
from app.schemas.relatorio_mapa import (
    RelatorioMapaCreate,
    RelatorioMapaUpdate,
    RelatorioMapaResponse,
    RelatorioMapaCSVRow,
    RelatorioMapaListResponse,
    RelatorioMapaMunicipalMensal
)
from app.utils.security import get_current_user


router = APIRouter(
    prefix="/api/relatorio-mapa",
    tags=["relatorio-mapa"]
)


from app.redis_cache import cache_response

@router.get("/agregacao-municipal-mensal", response_model=List[RelatorioMapaMunicipalMensal])
@cache_response(expire=3600)  # Agregação muda pouco, cache de 1 hora
def get_agregacao_municipal_mensal(
    id_programa: str,
    ano: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Retorna somatória mensal de inspeções por município, programa e ano.
    
    Agrupa por município e conta inspeções por status (NORMAL, SUSPEITA, POSITIVO)
    em cada mês do ano (N1-N12, S1-S12, P1-P12).
    
    Todos os campos são retornados, mesmo com valor zero.
    """
    # Query para buscar dados filtrados
    query = db.query(RelatorioMapa).options(
        joinedload(RelatorioMapa.programa_data)
    ).filter(
        RelatorioMapa.id_programa == id_programa,
        RelatorioMapa.ano == ano
    )
    
    relatorios = query.all()
    
    # Dicionário para agregar dados por município
    agregacao = {}
    
    for relatorio in relatorios:
        municipio = relatorio.municipio or "Não Informado"
        
        # Inicializar município se não existir
        if municipio not in agregacao:
            agregacao[municipio] = {
                'id_programa': id_programa,
                'municipio': municipio,
                'programa_data': relatorio.programa_data,
                **{f'N{i}': 0 for i in range(1, 13)},
                'NT': 0,
                **{f'S{i}': 0 for i in range(1, 13)},
                'ST': 0,
                **{f'P{i}': 0 for i in range(1, 13)},
                'PT': 0,
            }
        
        # Extrair mês da data
        try:
            # Assumindo formato YYYY-MM-DD ou similar
            if relatorio.data:
                mes = int(relatorio.data.split('-')[1])
            else:
                continue
        except (ValueError, IndexError, AttributeError):
            continue
        
        # Validar mês (1-12)
        if mes < 1 or mes > 12:
            continue
        
        # Classificar status e incrementar contador
        status_upper = (relatorio.status or "").upper()
        
        if status_upper == "NORMAL":
            agregacao[municipio][f'N{mes}'] += 1
            agregacao[municipio]['NT'] += 1
        elif status_upper == "SUSPEITA":
            agregacao[municipio][f'S{mes}'] += 1
            agregacao[municipio]['ST'] += 1
        elif status_upper in ("POSITIVO", "FOCO"):
            agregacao[municipio][f'P{mes}'] += 1
            agregacao[municipio]['PT'] += 1
    
    # Converter para lista de objetos
    resultado = list(agregacao.values())

    # Attach municipio/uf info when possible (best-effort; matches by name)
    # Attach municipio/uf info in batch (best-effort; match by name)
    municipio_names = [item.get('municipio') for item in resultado if item.get('municipio')]
    if municipio_names:
        unique_names = list(set(municipio_names))
        municipios = db.query(Municipio).filter(Municipio.nome.in_(unique_names)).all()
        municipios_by_name = {m.nome: m for m in municipios}
        estado_ids = {m.estado_id for m in municipios}
        estados = {}
        if estado_ids:
            ests = db.query(Estado).filter(Estado.id.in_(list(estado_ids))).all()
            estados = {e.id: e for e in ests}

        for item in resultado:
            municipio_name = item.get('municipio')
            if not municipio_name:
                continue
            m = municipios_by_name.get(municipio_name)
            if m:
                item['municipio_info'] = m
                est = estados.get(m.estado_id)
                if est:
                    item['uf_info'] = est

    return resultado


@router.get("/", response_model=List[RelatorioMapaListResponse])
@cache_response(expire=300)
def get_relatorios_mapa(
    skip: int = 0,
    limit: int = 100,
    id_programa: Optional[str] = None,
    ano: Optional[str] = None,
    trimestre: Optional[int] = None,
    municipio: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Listar relatórios de mapa com filtros simples.
    Não retorna o campo `coordenada` na listagem.
    """
    query = db.query(RelatorioMapa).options(
        joinedload(RelatorioMapa.programa_data),
        joinedload(RelatorioMapa.orgao_data),
        joinedload(RelatorioMapa.usuario_data),
        joinedload(RelatorioMapa.propriedade_data)
    )

    # Aplicar filtros conforme fornecidos
    if id_programa:
        query = query.filter(RelatorioMapa.id_programa == id_programa)
    if ano:
        query = query.filter(RelatorioMapa.ano == ano)
    if trimestre is not None:
        query = query.filter(RelatorioMapa.trimestre == trimestre)
    if municipio:
        query = query.filter(RelatorioMapa.municipio == municipio)

    relatorios = query.offset(skip).limit(limit).all()
    attach_location_info_batch(relatorios, db)
    return relatorios


@router.get("/{relatorio_id}", response_model=RelatorioMapaResponse)
def get_relatorio_mapa(
    relatorio_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Obter um relatório de mapa específico por `id` (INT)."""
    relatorio = db.query(RelatorioMapa).options(
        joinedload(RelatorioMapa.programa_data),
        joinedload(RelatorioMapa.orgao_data),
        joinedload(RelatorioMapa.usuario_data),
        joinedload(RelatorioMapa.propriedade_data)
    ).filter(RelatorioMapa.id == relatorio_id).first()

    if not relatorio:
        raise HTTPException(status_code=404, detail="Relatório de mapa não encontrado")

    # Converter campo POINT para texto legível (por id)
    result = db.execute(
        text("SELECT ST_AsText(coordenada) FROM relatorio_mapa WHERE id = :id"),
        {"id": relatorio.id}
    ).fetchone()
    if result and result[0]:
        relatorio.coordenada = result[0]

    attach_location_info(relatorio, db)
    return relatorio


@router.post(
    "/",
    response_model=RelatorioMapaResponse,
    status_code=status.HTTP_201_CREATED
)
def create_relatorio_mapa(
    relatorio: RelatorioMapaCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Criar novo relatório de mapa

    Campos id, ano e trimestre são calculados automaticamente via trigger.
    Valida FKs e gera campo POINT a partir de latitude/longitude.
    """
    # Validar se programa existe
    programa = db.query(Programa).filter(
        Programa.id == relatorio.id_programa
    ).first()
    if not programa:
        raise HTTPException(
            status_code=404,
            detail="Programa não encontrado"
        )

    # Validar se propriedade existe (opcional)
    if relatorio.id_propriedade:
        propriedade = db.query(Propriedade).filter(
            Propriedade.id == relatorio.id_propriedade
        ).first()
        if not propriedade:
            raise HTTPException(
                status_code=404,
                detail="Propriedade não encontrada"
            )

    # Validar se órgão existe (opcional)
    if relatorio.orgao:
        orgao = db.query(Orgao).filter(Orgao.id == relatorio.orgao).first()
        if not orgao:
            raise HTTPException(
                status_code=404,
                detail="Órgão não encontrado"
            )

    # Validar se usuário existe (opcional)
    if relatorio.id_usuario:
        usuario = db.query(User).filter(
            User.login == relatorio.id_usuario
        ).first()
        if not usuario:
            raise HTTPException(
                status_code=404,
                detail="Usuário não encontrado"
            )

    # Validar se termo de inspeção existe (opcional)
    if relatorio.termo_inspecao:
        db.query(TermoInspecao).filter(
            TermoInspecao.id == str(relatorio.termo_inspecao)
        ).first()
        # Não retorna erro se não encontrar, apenas warning

    db_relatorio = RelatorioMapa(
        **relatorio.model_dump()
    )
    db.add(db_relatorio)
    db.commit()

    # Recarregar com relacionamentos
    db.refresh(db_relatorio, [
        "programa_data", "orgao_data",
        "usuario_data", "propriedade_data"
    ])

    return db_relatorio


@router.patch("/{relatorio_id}", response_model=RelatorioMapaResponse)
def update_relatorio_mapa(
    relatorio_id: int,
    relatorio: RelatorioMapaUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Atualizar relatório de mapa (PATCH - apenas campos fornecidos)"""
    db_relatorio = db.query(RelatorioMapa).filter(RelatorioMapa.id == relatorio_id).first()

    if not db_relatorio:
        raise HTTPException(
            status_code=404,
            detail="Relatório de mapa não encontrado"
        )

    # Atualiza apenas os campos fornecidos
    update_data = relatorio.model_dump(exclude_unset=True)

    # Validações de FK se fornecidos
    if 'id_propriedade' in update_data:
        propriedade = db.query(Propriedade).filter(
            Propriedade.id == update_data['id_propriedade']
        ).first()
        if not propriedade:
            raise HTTPException(
                status_code=404,
                detail="Propriedade não encontrada"
            )

    if 'orgao' in update_data:
        orgao = db.query(Orgao).filter(
            Orgao.id == update_data['orgao']
        ).first()
        if not orgao:
            raise HTTPException(
                status_code=404,
                detail="Órgão não encontrado"
            )

    if 'id_usuario' in update_data:
        usuario = db.query(User).filter(
            User.login == update_data['id_usuario']
        ).first()
        if not usuario:
            raise HTTPException(
                status_code=404,
                detail="Usuário não encontrado"
            )

        # Atualizar normalmente sem mexer no POINT
        for field, value in update_data.items():
            setattr(db_relatorio, field, value)
        db.commit()

    db.refresh(db_relatorio, ["programa_data", "orgao_data", "usuario_data", "propriedade_data"])

    # Converter campo POINT para texto legível (por id)
    result = db.execute(text("SELECT ST_AsText(coordenada) FROM relatorio_mapa WHERE id = :id"), {"id": db_relatorio.id}).fetchone()
    if result and result[0]:
        db_relatorio.coordenada = result[0]

    return db_relatorio


@router.delete("/{relatorio_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_relatorio_mapa(
    relatorio_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Deletar um relatório de mapa por `id` (INT)."""
    db_relatorio = db.query(RelatorioMapa).filter(RelatorioMapa.id == relatorio_id).first()

    if not db_relatorio:
        raise HTTPException(status_code=404, detail="Relatório de mapa não encontrado")

    db.delete(db_relatorio)
    db.commit()
    return None


@router.post("/import-csv", status_code=status.HTTP_201_CREATED)
async def import_csv_relatorio_mapa(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Importar relatórios de mapa via arquivo CSV

    O arquivo CSV deve conter as colunas:
    id_programa, data, orgao, id_usuario, termo_inspecao, termo_coleta,
    id_propriedade, tipo_imovel, municipio, cultura, status,
    latitude, longitude

    Os campos id, ano e trimestre são calculados automaticamente por trigger.
    
    O delimitador (vírgula ou ponto e vírgula) é detectado automaticamente.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="Arquivo deve ser CSV"
        )

    # Ler conteúdo do arquivo
    contents = await file.read()
    
    # Tentar decodificar com diferentes encodings (incluindo UTF-8-BOM)
    try:
        csv_content = contents.decode('utf-8-sig')  # Remove BOM automaticamente
    except UnicodeDecodeError:
        try:
            csv_content = contents.decode('utf-8')
        except UnicodeDecodeError:
            try:
                csv_content = contents.decode('latin-1')
            except UnicodeDecodeError:
                csv_content = contents.decode('cp1252')
    
    # Detectar delimitador do CSV (vírgula ou ponto e vírgula)
    csv_data = io.StringIO(csv_content)
    sniffer = csv.Sniffer()
    sample = csv_content[:1024]  # Amostra dos primeiros 1024 caracteres
    try:
        delimiter = sniffer.sniff(sample).delimiter
    except Exception:
        # Se falhar a detecção, tenta ponto e vírgula primeiro, depois vírgula
        delimiter = ';' if ';' in sample else ','
    
    csv_data.seek(0)  # Voltar ao início do StringIO
    csv_reader = csv.DictReader(csv_data, delimiter=delimiter)

    imported_count = 0
    errors = []

    for row_num, row in enumerate(csv_reader, start=2):
        try:
            # Limpar o dicionário removendo chaves None ou vazias
            # Converter valores vazios, "-", "null", etc em None
            cleaned_row = {}
            for k, v in row.items():
                if not k or not k.strip():
                    continue
                key = k.strip()
                value = v.strip() if v else ''
                # Converter valores vazios em None para campos opcionais
                if value in ('', '-', 'null', 'NULL', 'None'):
                    # Campos opcionais que aceitam None
                    if key in ('id_propriedade', 'id_usuario', 'orgao',
                               'latitude', 'longitude'):
                        cleaned_row[key] = None
                    else:
                        cleaned_row[key] = value
                else:
                    cleaned_row[key] = value
            
            # Validar linha com Pydantic
            csv_row = RelatorioMapaCSVRow(**cleaned_row)

            # Validar FKs
            programa = db.query(Programa).filter(
                Programa.id == csv_row.id_programa
            ).first()
            if not programa:
                errors.append({
                    "row": row_num,
                    "error": f"Programa {csv_row.id_programa} não encontrado"
                })
                continue

            # Validar propriedade (opcional)
            if csv_row.id_propriedade:
                propriedade = db.query(Propriedade).filter(
                    Propriedade.id == csv_row.id_propriedade
                ).first()
                if not propriedade:
                    errors.append({
                        "row": row_num,
                        "error": (
                            f"Propriedade {csv_row.id_propriedade} "
                            "não encontrada"
                        )
                    })
                    continue

            # Inserir registro com ORM
            db_relatorio = RelatorioMapa(**csv_row.model_dump())
            db.add(db_relatorio)
            imported_count += 1

        except Exception as e:
            errors.append({
                "row": row_num,
                "error": str(e)
            })
            continue

    # Commit all inserts
    db.commit()

    return {
        "message": "Import completed",
        "imported": imported_count,
        "errors": errors
    }
