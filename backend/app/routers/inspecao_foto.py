"""
Router: Fotos Georreferenciadas de Inspeção
============================================
Endpoint principal:
  POST /api/inspecoes/foto/{id_area_programa}
    - Recebe arquivo de imagem via multipart/form-data
    - Extrai coordenadas GPS do cabeçalho EXIF (biblioteca `exif`)
    - Salva o arquivo em storage/fotos/{ano}/{mes}/{dia}/{uuid}.jpg
    - Persiste o registro no banco de dados (PostGIS)

Endpoints auxiliares:
  GET  /api/inspecoes/foto/{id_area_programa}        — lista fotos de um AreaPrograma
  GET  /api/inspecoes/foto/detalhe/{foto_id}         — detalhe de uma foto
  DELETE /api/inspecoes/foto/detalhe/{foto_id}       — remove foto (arquivo + registro)
"""

from __future__ import annotations

import os
import uuid
import logging
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.area_programa import AreaPrograma
from app.models.inspecao_foto import InspecaoFoto
from app.schemas.inspecao_foto import InspecaoFotoResponse, InspecaoFotoUploadResponse
from app.utils.security import get_current_user
from app.models.users import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/inspecoes/foto", tags=["Fotos Georreferenciadas"])

# ---------------------------------------------------------------------------
# Diretório base de armazenamento
# ---------------------------------------------------------------------------
# Resolve em relação à raiz do projeto (onde main.py está)
_BASE_DIR = Path(__file__).resolve().parent.parent.parent  # raiz do projeto
STORAGE_BASE = _BASE_DIR / "storage" / "fotos"

# Extensões permitidas
EXTENSOES_PERMITIDAS = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".tiff", ".tif"}


# ---------------------------------------------------------------------------
# Helpers: EXIF
# ---------------------------------------------------------------------------

def _gms_para_decimal(graus: float, minutos: float, segundos: float, ref: str) -> Decimal:
    """
    Converte coordenadas GMS (Graus, Minutos, Segundos) para Decimal.
    Aplica sinal negativo para referências S (Sul) e W (Oeste).
    """
    decimal = Decimal(str(graus)) + Decimal(str(minutos)) / 60 + Decimal(str(segundos)) / 3600
    if ref.upper() in ("S", "W"):
        decimal = -decimal
    return decimal.quantize(Decimal("0.000000001"))


def _extrair_coordenadas_exif(conteudo: bytes) -> tuple[Optional[Decimal], Optional[Decimal], Optional[datetime]]:
    """
    Tenta extrair latitude, longitude e data/hora de captura dos metadados EXIF.
    Retorna (latitude, longitude, data_captura) — qualquer um pode ser None.
    """
    latitude = None
    longitude = None
    data_captura = None

    try:
        from exif import Image as ExifImage  # importação lazy — evita erro se não instalado

        img = ExifImage(conteudo)

        if not img.has_exif:
            return latitude, longitude, data_captura

        # ── Coordenadas GPS ────────────────────────────────────────────────
        try:
            lat_gms = img.gps_latitude          # tupla (graus, minutos, segundos)
            lat_ref = img.gps_latitude_ref      # 'N' ou 'S'
            lon_gms = img.gps_longitude
            lon_ref = img.gps_longitude_ref     # 'E' ou 'W'

            latitude  = _gms_para_decimal(*lat_gms, lat_ref)
            longitude = _gms_para_decimal(*lon_gms, lon_ref)
        except (AttributeError, Exception) as exc:
            logger.debug("EXIF: coordenadas GPS ausentes ou inválidas — %s", exc)

        # ── Data/hora de captura ───────────────────────────────────────────
        try:
            # Formato EXIF: 'YYYY:MM:DD HH:MM:SS'
            dt_str: str = img.datetime_original or img.datetime
            if dt_str:
                data_captura = datetime.strptime(dt_str, "%Y:%m:%d %H:%M:%S")
        except (AttributeError, ValueError, Exception) as exc:
            logger.debug("EXIF: data de captura ausente ou inválida — %s", exc)

    except ImportError:
        logger.warning(
            "Biblioteca 'exif' não instalada. "
            "Execute: pip install exif  — metadados EXIF não serão extraídos."
        )
    except Exception as exc:
        logger.warning("Falha ao processar EXIF: %s", exc)

    return latitude, longitude, data_captura


# ---------------------------------------------------------------------------
# Endpoint: Upload de foto
# ---------------------------------------------------------------------------

@router.post(
    "/{id_area_programa}",
    response_model=InspecaoFotoUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload de foto georreferenciada",
    description=(
        "Recebe uma imagem via multipart/form-data, extrai coordenadas GPS do EXIF "
        "e persiste o registro vinculado ao AreaPrograma informado."
    ),
)
async def upload_foto(
    id_area_programa: str,
    arquivo: UploadFile = File(..., description="Arquivo de imagem (JPEG, PNG, HEIC, TIFF)"),
    descricao: Optional[str] = Form(None, description="Descrição opcional da foto"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ── 1. Valida existência do AreaPrograma ───────────────────────────────
    area_programa = db.get(AreaPrograma, id_area_programa)
    if not area_programa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AreaPrograma '{id_area_programa}' não encontrado.",
        )

    # ── 2. Valida extensão do arquivo ──────────────────────────────────────
    nome_original = arquivo.filename or "sem_nome"
    _, ext = os.path.splitext(nome_original)
    ext = ext.lower()

    if ext not in EXTENSOES_PERMITIDAS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Extensão '{ext}' não permitida. "
                f"Use: {', '.join(sorted(EXTENSOES_PERMITIDAS))}"
            ),
        )

    # ── 3. Lê o conteúdo do arquivo ────────────────────────────────────────
    conteudo = await arquivo.read()

    # ── 4. Extrai metadados EXIF ───────────────────────────────────────────
    latitude, longitude, data_captura_exif = _extrair_coordenadas_exif(conteudo)
    exif_extraido = latitude is not None and longitude is not None
    
    # ── 4.5 Injeta marca d'agua de Autoria ────────────────────────────────
    try:
        from PIL import Image, ImageDraw
        import io
        
        with Image.open(io.BytesIO(conteudo)) as img:
            exif_data = img.info.get('exif')
            draw = ImageDraw.Draw(img)
            
            author_text = f"Autor: {current_user.nome or current_user.login}"
            if current_user.matricula:
                author_text += f" - Mat: {current_user.matricula}"
                
            # Adiciona texto no canto inferior esquerdo
            draw.text((10, img.height - 30), author_text, fill="white")
            
            out_io = io.BytesIO()
            if exif_data:
                img.save(out_io, format=img.format or 'JPEG', exif=exif_data)
            else:
                img.save(out_io, format=img.format or 'JPEG')
                
            conteudo = out_io.getvalue()
    except Exception as exc:
        logger.error(f"Erro ao injetar marca d'agua na foto: {exc}")


    # ── 5. Define caminho de armazenamento com data atual ──────────────────
    agora = datetime.utcnow()
    subdir = STORAGE_BASE / str(agora.year) / f"{agora.month:02d}" / f"{agora.day:02d}"
    subdir.mkdir(parents=True, exist_ok=True)

    foto_id = str(uuid.uuid4())
    nome_arquivo_salvo = f"{foto_id}{ext}"
    caminho_absoluto = subdir / nome_arquivo_salvo

    # Caminho relativo (para armazenar no banco e servir via URL)
    caminho_relativo = (
        f"storage/fotos/{agora.year}/{agora.month:02d}/{agora.day:02d}/{nome_arquivo_salvo}"
    )

    # ── 6. Salva o arquivo em disco ────────────────────────────────────────
    try:
        caminho_absoluto.write_bytes(conteudo)
    except OSError as exc:
        logger.error("Erro ao salvar arquivo em disco: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao salvar o arquivo. Tente novamente.",
        )

    # ── 7. Persiste registro no banco ──────────────────────────────────────
    data_captura_final = data_captura_exif or agora

    db_foto = InspecaoFoto(
        id=foto_id,
        id_area_programa=id_area_programa,
        arquivo_nome=nome_original[:255],          # trunca se necessário
        arquivo_path=caminho_relativo,
        latitude=latitude,
        longitude=longitude,
        data_captura=data_captura_final,
        descricao=descricao[:255] if descricao else None,
        id_usuario=current_user.id,
        status_homologacao='aberto'
    )

    db.add(db_foto)
    db.commit()
    db.refresh(db_foto)

    logger.info(
        "Foto salva — id=%s | area_programa=%s | exif=%s | lat=%s | lon=%s",
        foto_id, id_area_programa, exif_extraido, latitude, longitude,
    )

    return InspecaoFotoUploadResponse(
        id=foto_id,
        arquivo_nome=nome_original,
        arquivo_path=caminho_relativo,
        latitude=latitude,
        longitude=longitude,
        data_captura=data_captura_final,
        exif_extraido=exif_extraido,
        message="Foto enviada e registrada com sucesso.",
    )


# ---------------------------------------------------------------------------
# Endpoint: Listar fotos de um AreaPrograma
# ---------------------------------------------------------------------------

@router.get(
    "/{id_area_programa}",
    response_model=List[InspecaoFotoResponse],
    summary="Lista fotos de um AreaPrograma",
)
def listar_fotos(
    id_area_programa: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    area_programa = db.get(AreaPrograma, id_area_programa)
    if not area_programa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AreaPrograma '{id_area_programa}' não encontrado.",
        )

    fotos = (
        db.query(InspecaoFoto)
        .filter(InspecaoFoto.id_area_programa == id_area_programa)
        .order_by(InspecaoFoto.data_captura.desc())
        .all()
    )

    return [
        InspecaoFotoResponse(
            **{c.key: getattr(f, c.key) for c in f.__table__.columns},
            exif_extraido=(f.latitude is not None and f.longitude is not None),
        )
        for f in fotos
    ]


# ---------------------------------------------------------------------------
# Endpoint: Detalhe de uma foto
# ---------------------------------------------------------------------------

@router.get(
    "/detalhe/{foto_id}",
    response_model=InspecaoFotoResponse,
    summary="Detalhe de uma foto georreferenciada",
)
def detalhe_foto(
    foto_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    foto = db.get(InspecaoFoto, foto_id)
    if not foto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Foto '{foto_id}' não encontrada.",
        )
        
    # Auditoria Técnica (O-BAC) - Log de visualização de conteúdo sensível
    from app.models.auditoria_acesso import AuditoriaAcesso
    import uuid
    from datetime import datetime
    
    # Registra quem viu, quando e o que (id da foto e da area programa afetada)
    log_auditoria = AuditoriaAcesso(
        id=uuid.uuid4().hex,
        id_usuario=current_user.id,
        recurso_acessado=f"inspecao_foto_detalhe/{foto_id}",
        tipo_acao="GET",
        data_hora=datetime.utcnow(),
        ip_origem=request.client.host if request.client else "desconhecido",
    )
    db.add(log_auditoria)
    db.commit()

    return InspecaoFotoResponse(
        **{c.key: getattr(foto, c.key) for c in foto.__table__.columns},
        exif_extraido=(foto.latitude is not None and foto.longitude is not None),
    )


# ---------------------------------------------------------------------------
# Endpoint: Remover foto
# ---------------------------------------------------------------------------

@router.delete(
    "/detalhe/{foto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove uma foto georreferenciada (arquivo + registro)",
)
def remover_foto(
    foto_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    foto = db.get(InspecaoFoto, foto_id)
    if not foto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Foto '{foto_id}' não encontrada.",
        )

    # Remove arquivo físico (ignora silenciosamente se já não existir)
    arquivo_fisico = _BASE_DIR / foto.arquivo_path
    try:
        arquivo_fisico.unlink(missing_ok=True)
    except OSError as exc:
        logger.warning("Não foi possível remover arquivo físico '%s': %s", arquivo_fisico, exc)

    db.delete(foto)
    db.commit()
