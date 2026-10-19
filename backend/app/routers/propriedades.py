from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
import uuid

from app.config.database import get_db
from app.models.propriedade import Propriedade
from app.schemas.propriedade import (
    PropriedadeCreate, PropriedadeUpdate, PropriedadeResponse
)
from app.utils.security import get_current_user

router = APIRouter(
    prefix="/api/propriedades",
    tags=["propriedades"]
)


def build_coordenada_text(propriedade: Propriedade) -> None:
    """Monta um POINT textual sem depender de coluna geometrica."""
    if propriedade.latitude is None or propriedade.longitude is None:
        propriedade.coordenada = None
        return

    propriedade.coordenada = f"POINT({propriedade.longitude} {propriedade.latitude})"


from app.redis_cache import cache_response

@router.get("/", response_model=List[PropriedadeResponse])
@cache_response(expire=300)
def get_propriedades(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Listar todas as propriedades com dados do proprietario."""
    propriedades = db.query(Propriedade).options(
        joinedload(Propriedade.proprietario_data)
    ).offset(skip).limit(limit).all()

    for prop in propriedades:
        build_coordenada_text(prop)

    from app.services.locations import attach_location_info_batch
    attach_location_info_batch(propriedades, db)

    return propriedades


@router.get("/{propriedade_id}", response_model=PropriedadeResponse)
def get_propriedade(
    propriedade_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Obter uma propriedade especifica com dados do proprietario."""
    propriedade = db.query(Propriedade).options(
        joinedload(Propriedade.proprietario_data)
    ).filter(Propriedade.id == propriedade_id).first()

    if not propriedade:
        raise HTTPException(
            status_code=404,
            detail="Propriedade nao encontrada"
        )

    build_coordenada_text(propriedade)

    from app.services.locations import attach_location_info
    attach_location_info(propriedade, db)

    return propriedade


@router.post(
    "/",
    response_model=PropriedadeResponse,
    status_code=status.HTTP_201_CREATED
)
def create_propriedade(
    propriedade: PropriedadeCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Criar nova propriedade."""
    new_id = uuid.uuid4().hex[:18]

    db_propriedade = Propriedade(
        id=new_id,
        **propriedade.model_dump()
    )

    db.add(db_propriedade)
    db.commit()
    db.refresh(db_propriedade, ["proprietario_data"])
    build_coordenada_text(db_propriedade)

    return db_propriedade


@router.patch("/{propriedade_id}", response_model=PropriedadeResponse)
def update_propriedade(
    propriedade_id: str,
    propriedade: PropriedadeUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Atualizar uma propriedade (PATCH - apenas campos fornecidos)."""
    db_propriedade = db.query(Propriedade).filter(
        Propriedade.id == propriedade_id
    ).first()

    if not db_propriedade:
        raise HTTPException(
            status_code=404,
            detail="Propriedade nao encontrada"
        )

    update_data = propriedade.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_propriedade, field, value)

    db.commit()
    db.refresh(db_propriedade, ["proprietario_data"])
    build_coordenada_text(db_propriedade)

    return db_propriedade


@router.delete("/{propriedade_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_propriedade(
    propriedade_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Deletar uma propriedade."""
    db_propriedade = db.query(Propriedade).filter(
        Propriedade.id == propriedade_id
    ).first()

    if not db_propriedade:
        raise HTTPException(
            status_code=404,
            detail="Propriedade nao encontrada"
        )

    db.delete(db_propriedade)
    db.commit()
    return None
