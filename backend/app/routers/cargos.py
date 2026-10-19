from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import uuid

from app.config.database import get_db
from app.models.cargo import Cargo
from app.schemas.cargo import CargoCreate, CargoUpdate, CargoResponse
from app.schemas.common import MessageResponse
from app.utils.security import get_current_user
from app.models.users import User

router = APIRouter(prefix="/api/cargos", tags=["cargos"])


@router.get("/", response_model=List[CargoResponse])
def get_cargos(
    id_orgao: Optional[str] = Query(None, description="Filtrar cargos por órgão"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Cargo).options(joinedload(Cargo.orgao_data))
    if id_orgao:
        query = query.filter(Cargo.id_orgao == id_orgao)
    return query.offset(skip).limit(limit).all()


@router.get("/{cargo_id}", response_model=CargoResponse)
def get_cargo(
    cargo_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cargo = db.query(Cargo).options(
        joinedload(Cargo.orgao_data)
    ).filter(Cargo.id == cargo_id).first()

    if not cargo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cargo não encontrado")

    return cargo


@router.post("/", response_model=CargoResponse, status_code=status.HTTP_201_CREATED)
def create_cargo(
    cargo_in: CargoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_id = cargo_in.id or str(uuid.uuid4())

    db_cargo = Cargo(
        id=new_id,
        id_orgao=cargo_in.id_orgao,
        sigla=cargo_in.sigla,
        nome=cargo_in.nome,
        descricao=cargo_in.descricao,
    )

    db.add(db_cargo)
    db.commit()
    db.refresh(db_cargo, ['orgao_data'])
    return db_cargo


@router.patch("/{cargo_id}", response_model=CargoResponse)
def update_cargo(
    cargo_id: str,
    cargo_in: CargoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_cargo = db.query(Cargo).filter(Cargo.id == cargo_id).first()

    if not db_cargo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cargo não encontrado")

    for field, value in cargo_in.model_dump(exclude_unset=True).items():
        setattr(db_cargo, field, value)

    db.commit()
    db.refresh(db_cargo, ['orgao_data'])
    return db_cargo


@router.delete("/{cargo_id}", response_model=MessageResponse)
def delete_cargo(
    cargo_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_cargo = db.query(Cargo).filter(Cargo.id == cargo_id).first()

    if not db_cargo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cargo não encontrado")

    db.delete(db_cargo)
    db.commit()
    return MessageResponse(message="Cargo deletado com sucesso")
