from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from app.config.database import get_db
from app.models.reg_atividade import RegAtividade
from app.schemas.reg_atividade import (
    RegAtividadeCreate,
    RegAtividadeUpdate,
    RegAtividadeResponse,
)
from app.schemas.common import MessageResponse
from app.utils.security import get_current_user
from app.models.users import User

router = APIRouter(
    prefix="/api/reg-atividade",
    tags=["reg-atividade"],
)


@router.get("/", response_model=List[RegAtividadeResponse])
def get_reg_atividades(
    programa: Optional[str] = Query(None, description="Filtrar por programa"),
    user: Optional[str] = Query(None, description="Filtrar por usuário"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Listar registros de atividade."""
    query = db.query(RegAtividade).options(joinedload(RegAtividade.programa_data))
    if programa:
        query = query.filter(RegAtividade.programa == programa)
    if user:
        query = query.filter(RegAtividade.user == user)
    registros = query.offset(skip).limit(limit).all()
    return registros


@router.get("/{reg_id}", response_model=RegAtividadeResponse)
def get_reg_atividade(
    reg_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obter um registro de atividade pelo ID."""
    reg = (
        db.query(RegAtividade)
        .options(joinedload(RegAtividade.programa_data))
        .filter(RegAtividade.id == reg_id)
        .first()
    )
    if not reg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro de atividade não encontrado",
        )
    return reg


@router.post("/", response_model=RegAtividadeResponse, status_code=status.HTTP_201_CREATED)
def create_reg_atividade(
    reg: RegAtividadeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Criar novo registro de atividade."""
    db_reg = RegAtividade(**reg.model_dump())
    db.add(db_reg)
    db.commit()
    db.refresh(db_reg, ["programa_data"])
    return db_reg


@router.patch("/{reg_id}", response_model=RegAtividadeResponse)
def update_reg_atividade(
    reg_id: int,
    reg: RegAtividadeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Atualizar registro de atividade (PATCH)."""
    db_reg = db.query(RegAtividade).filter(RegAtividade.id == reg_id).first()
    if not db_reg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro de atividade não encontrado",
        )
    update_data = reg.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_reg, field, value)
    db.commit()
    db.refresh(db_reg, ["programa_data"])
    return db_reg


@router.delete("/{reg_id}", response_model=MessageResponse)
def delete_reg_atividade(
    reg_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Deletar registro de atividade."""
    db_reg = db.query(RegAtividade).filter(RegAtividade.id == reg_id).first()
    if not db_reg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro de atividade não encontrado",
        )
    db.delete(db_reg)
    db.commit()
    return MessageResponse(message="Registro de atividade deletado com sucesso")
