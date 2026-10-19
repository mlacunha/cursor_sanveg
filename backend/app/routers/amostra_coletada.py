from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.config.database import get_db
from app.models.amostra_coletada import AmostraColetada
from app.models.area_programa import AreaPrograma
from app.schemas.amostra_coletada import (
    AmostraColetadaCreate,
    AmostraColetadaUpdate,
    AmostraColetadaResponse,
)
from app.schemas.common import MessageResponse
from app.utils.security import get_current_user
from app.models.users import User

router = APIRouter(
    prefix="/api/amostra-coletada",
    tags=["amostra-coletada"],
)

LAUDOS_DIR = Path(__file__).resolve().parents[2] / "uploads" / "laudos"
LAUDOS_DIR.mkdir(parents=True, exist_ok=True)
MAX_LAUDO_SIZE = 10 * 1024 * 1024
VALID_RESULTADOS_LAB = {
    "NEGATIVO",
    "POSITIVO",
    "INCONCLUSIVO",
    "AMOSTRA_REJEITADA",
    "AMOSTRA_INVALIDA",
}


def _normalize_resultado_laboratorio(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None

    normalized = value.strip().upper()
    if not normalized:
        return None

    normalized = {
        "AMOSTRA REJEITADA": "AMOSTRA_REJEITADA",
        "AMOSTRA INVALIDA": "AMOSTRA_INVALIDA",
    }.get(normalized, normalized)

    if normalized not in VALID_RESULTADOS_LAB:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="resultado_laboratorio invalido",
        )

    return normalized


def _apply_area_programa_resultado_from_lab(
    db: Session,
    amostra: AmostraColetada,
    previous_resultado: Optional[str],
    next_resultado: Optional[str],
) -> None:
    normalized_previous = _normalize_resultado_laboratorio(previous_resultado)
    normalized_next = _normalize_resultado_laboratorio(next_resultado)

    if not amostra.data_resultado or not normalized_next or normalized_previous == normalized_next:
        return

    mapped_resultado = None
    if normalized_next == "POSITIVO":
        mapped_resultado = "POSITIVO"
    elif normalized_next == "NEGATIVO":
        mapped_resultado = "NORMAL"

    if mapped_resultado is None:
        return

    ap = db.query(AreaPrograma).filter(AreaPrograma.id == amostra.id_area_programa).first()
    if not ap:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="area_programa vinculada a amostra nao encontrada",
        )

    if ap.resultado != mapped_resultado:
        ap.resultado = mapped_resultado


@router.get("/", response_model=List[AmostraColetadaResponse])
def get_amostras_coletadas(
    id_area_programa: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 200,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(AmostraColetada)
    if id_area_programa:
        query = query.filter(AmostraColetada.id_area_programa == id_area_programa)
    return query.offset(skip).limit(limit).all()


@router.get("/{amostra_id}", response_model=AmostraColetadaResponse)
def get_amostra_coletada(
    amostra_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    amostra = db.query(AmostraColetada).filter(AmostraColetada.id == amostra_id).first()
    if not amostra:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Amostra não encontrada")
    return amostra


@router.post("/", response_model=AmostraColetadaResponse, status_code=status.HTTP_201_CREATED)
def create_amostra_coletada(
    body: AmostraColetadaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ap = db.query(AreaPrograma).filter(AreaPrograma.id == body.id_area_programa).first()
    if not ap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro area_programa não encontrado",
        )
    payload = body.model_dump()
    if not payload.get("id"):
        payload["id"] = str(uuid.uuid4())
    payload["resultado_laboratorio"] = _normalize_resultado_laboratorio(
        payload.get("resultado_laboratorio")
    )

    db_amostra = AmostraColetada(**payload)
    db.add(db_amostra)
    _apply_area_programa_resultado_from_lab(
        db=db,
        amostra=db_amostra,
        previous_resultado=None,
        next_resultado=db_amostra.resultado_laboratorio,
    )
    db.commit()
    db.refresh(db_amostra)
    return db_amostra


@router.patch("/{amostra_id}", response_model=AmostraColetadaResponse)
def update_amostra_coletada(
    amostra_id: str,
    body: AmostraColetadaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_amostra = db.query(AmostraColetada).filter(AmostraColetada.id == amostra_id).first()
    if not db_amostra:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Amostra não encontrada")
    update_data = body.model_dump(exclude_unset=True)
    previous_resultado = db_amostra.resultado_laboratorio

    if "resultado_laboratorio" in update_data:
        update_data["resultado_laboratorio"] = _normalize_resultado_laboratorio(
            update_data.get("resultado_laboratorio")
        )

    for field, value in update_data.items():
        setattr(db_amostra, field, value)

    if "resultado_laboratorio" in update_data:
        _apply_area_programa_resultado_from_lab(
            db=db,
            amostra=db_amostra,
            previous_resultado=previous_resultado,
            next_resultado=db_amostra.resultado_laboratorio,
        )
    db.commit()
    db.refresh(db_amostra)
    return db_amostra


@router.post("/{amostra_id}/laudo", response_model=AmostraColetadaResponse)
async def upload_laudo_amostra(
    amostra_id: str,
    laudo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_amostra = db.query(AmostraColetada).filter(AmostraColetada.id == amostra_id).first()
    if not db_amostra:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Amostra nÃ£o encontrada")

    filename = (laudo.filename or "").lower()
    if laudo.content_type != "application/pdf" and not filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O laudo deve ser enviado em PDF",
        )

    content = await laudo.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo de laudo vazio",
        )
    if len(content) > MAX_LAUDO_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O laudo excede o limite de 10 MB",
        )

    new_filename = f"{amostra_id}_{uuid.uuid4().hex}.pdf"
    target_path = LAUDOS_DIR / new_filename
    target_path.write_bytes(content)

    old_path = db_amostra.laudo_arquivo or ""
    if old_path.startswith("/uploads/laudos/"):
        old_file = Path(__file__).resolve().parents[2] / Path(old_path.lstrip("/"))
        if old_file.exists() and old_file.is_file():
            old_file.unlink()

    db_amostra.laudo_arquivo = f"/uploads/laudos/{new_filename}"
    db.commit()
    db.refresh(db_amostra)
    await laudo.close()
    return db_amostra


@router.delete("/{amostra_id}", response_model=MessageResponse)
def delete_amostra_coletada(
    amostra_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_amostra = db.query(AmostraColetada).filter(AmostraColetada.id == amostra_id).first()
    if not db_amostra:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Amostra não encontrada")
    db.delete(db_amostra)
    db.commit()
    return MessageResponse(message="Amostra removida com sucesso")
