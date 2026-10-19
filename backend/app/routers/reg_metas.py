from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from app.config.database import get_db
from app.models.reg_metas import RegMetas
from app.schemas.reg_metas import RegMetasCreate, RegMetasUpdate, RegMetasResponse
from app.schemas.common import MessageResponse
from app.utils.security import get_current_user
from app.models.users import User

router = APIRouter(
    prefix="/api/reg-metas",
    tags=["reg-metas"],
)


@router.get("/", response_model=List[RegMetasResponse])
def get_reg_metas(
    programa: Optional[str] = Query(None, description="Filtrar por programa"),
    ano: Optional[int] = Query(None, description="Filtrar por ano"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Listar registros de metas."""
    query = db.query(RegMetas).options(joinedload(RegMetas.programa_data))
    if programa:
        query = query.filter(RegMetas.programa == programa)
    if ano is not None:
        query = query.filter(RegMetas.ano == ano)
    registros = query.offset(skip).limit(limit).all()
    return registros


@router.get("/{reg_id}", response_model=RegMetasResponse)
def get_reg_meta(
    reg_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obter um registro de meta pelo ID."""
    reg = (
        db.query(RegMetas)
        .options(joinedload(RegMetas.programa_data))
        .filter(RegMetas.id == reg_id)
        .first()
    )
    if not reg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro de meta não encontrado",
        )
    return reg


@router.post("/", response_model=RegMetasResponse, status_code=status.HTTP_201_CREATED)
def create_reg_meta(
    reg: RegMetasCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Criar novo registro de meta."""
    db_reg = RegMetas(**reg.model_dump())
    db.add(db_reg)
    db.commit()
    db.refresh(db_reg, ["programa_data"])
    return db_reg


@router.patch("/{reg_id}", response_model=RegMetasResponse)
def update_reg_meta(
    reg_id: int,
    reg: RegMetasUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Atualizar registro de meta (PATCH)."""
    db_reg = db.query(RegMetas).filter(RegMetas.id == reg_id).first()
    if not db_reg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro de meta não encontrado",
        )
    update_data = reg.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_reg, field, value)
    db.commit()
    db.refresh(db_reg, ["programa_data"])
    return db_reg


@router.delete("/{reg_id}", response_model=MessageResponse)
def delete_reg_meta(
    reg_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Deletar registro de meta."""
    db_reg = db.query(RegMetas).filter(RegMetas.id == reg_id).first()
    if not db_reg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro de meta não encontrado",
        )
    db.delete(db_reg)
    db.commit()
    return MessageResponse(message="Registro de meta deletado com sucesso")
