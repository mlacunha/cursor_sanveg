from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.config.database import get_db
from app.models.area_inspecionada import AreaInspecionada
from app.models.termo_inspecao import TermoInspecao
from app.schemas.area_inspecionada import (
    AreaInspecionadaCreate,
    AreaInspecionadaUpdate,
    AreaInspecionadaResponse,
)
from app.schemas.common import MessageResponse
from app.utils.security import get_current_user
from app.models.users import User

router = APIRouter(prefix="/api/area-inspecionada", tags=["area-inspecionada"])


@router.get("/", response_model=List[AreaInspecionadaResponse])
def get_areas_inspecionadas(
    id_termo_inspecao: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 200,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(AreaInspecionada)
    if id_termo_inspecao:
        query = query.filter(AreaInspecionada.id_termo_inspecao == id_termo_inspecao)
    return query.offset(skip).limit(limit).all()


@router.get("/{area_id}", response_model=AreaInspecionadaResponse)
def get_area_inspecionada(
    area_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    area = db.query(AreaInspecionada).filter(AreaInspecionada.id == area_id).first()
    if not area:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Área não encontrada")
    return area


@router.post("/", response_model=AreaInspecionadaResponse, status_code=status.HTTP_201_CREATED)
def create_area_inspecionada(
    area: AreaInspecionadaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    termo = db.query(TermoInspecao).filter(TermoInspecao.id == area.id_termo_inspecao).first()
    if not termo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Termo de inspeção não encontrado")

    data = area.model_dump()
    if not data.get("id"):
        data["id"] = str(uuid.uuid4())

    db_area = AreaInspecionada(**data)
    db.add(db_area)
    db.commit()
    db.refresh(db_area)
    return db_area


@router.patch("/{area_id}", response_model=AreaInspecionadaResponse)
def update_area_inspecionada(
    area_id: str,
    area: AreaInspecionadaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_area = db.query(AreaInspecionada).filter(AreaInspecionada.id == area_id).first()
    if not db_area:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Área não encontrada")
    for field, value in area.model_dump(exclude_unset=True).items():
        setattr(db_area, field, value)
    db.commit()
    db.refresh(db_area)
    return db_area


@router.delete("/{area_id}", response_model=MessageResponse)
def delete_area_inspecionada(
    area_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_area = db.query(AreaInspecionada).filter(AreaInspecionada.id == area_id).first()
    if not db_area:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Área não encontrada")
    db.delete(db_area)
    db.commit()
    return MessageResponse(message="Área inspecionada removida com sucesso")
