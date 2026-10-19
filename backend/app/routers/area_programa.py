from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import uuid

from app.config.database import get_db
from app.models.area_programa import AreaPrograma
from app.models.area_inspecionada import AreaInspecionada
from app.schemas.area_programa import (
    AreaProgramaCreate,
    AreaProgramaUpdate,
    AreaProgramaResponse,
)
from app.schemas.common import MessageResponse
from app.utils.security import get_current_user
from app.models.users import User

router = APIRouter(prefix="/api/area-programa", tags=["area-programa"])


@router.get("/", response_model=List[AreaProgramaResponse])
def get_area_programas(
    id_area: Optional[str] = Query(None),
    id_programa: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 200,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(AreaPrograma).options(joinedload(AreaPrograma.programa_data))
    if id_area:
        query = query.filter(AreaPrograma.id_area == id_area)
    if id_programa:
        query = query.filter(AreaPrograma.id_programa == id_programa)
    return query.offset(skip).limit(limit).all()


@router.get("/{ap_id}", response_model=AreaProgramaResponse)
def get_area_programa(
    ap_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ap = (
        db.query(AreaPrograma)
        .options(joinedload(AreaPrograma.programa_data))
        .filter(AreaPrograma.id == ap_id)
        .first()
    )
    if not ap:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro não encontrado")
    return ap


@router.post("/", response_model=AreaProgramaResponse, status_code=status.HTTP_201_CREATED)
def create_area_programa(
    body: AreaProgramaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    area = db.query(AreaInspecionada).filter(AreaInspecionada.id == body.id_area).first()
    if not area:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Área inspecionada não encontrada")

    data = body.model_dump()
    if not data.get("id"):
        data["id"] = str(uuid.uuid4())

    db_ap = AreaPrograma(**data)
    db.add(db_ap)
    db.commit()
    db.refresh(db_ap)
    db.refresh(db_ap, ["programa_data"])
    return db_ap


@router.patch("/{ap_id}", response_model=AreaProgramaResponse)
def update_area_programa(
    ap_id: str,
    body: AreaProgramaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_ap = db.query(AreaPrograma).filter(AreaPrograma.id == ap_id).first()
    if not db_ap:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro não encontrado")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(db_ap, field, value)
    db.commit()
    db.refresh(db_ap)
    db.refresh(db_ap, ["programa_data"])
    return db_ap


@router.delete("/{ap_id}", response_model=MessageResponse)
def delete_area_programa(
    ap_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_ap = db.query(AreaPrograma).filter(AreaPrograma.id == ap_id).first()
    if not db_ap:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro não encontrado")
    db.delete(db_ap)
    db.commit()
    return MessageResponse(message="Inspeção de programa removida com sucesso")
