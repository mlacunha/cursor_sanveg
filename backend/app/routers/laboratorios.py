from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.config.database import get_db
from app.models.laboratorio import Laboratorio
from app.schemas.laboratorio import (
    LaboratorioCreate,
    LaboratorioUpdate,
    LaboratorioResponse,
)
from app.schemas.common import MessageResponse
from app.utils.security import get_current_user
from app.models.users import User


router = APIRouter(
    prefix="/api/laboratorios",
    tags=["laboratorios"],
)


@router.get("/", response_model=List[LaboratorioResponse])
def listar_laboratorios(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista todos os laboratórios cadastrados."""
    labs = (
        db.query(Laboratorio)
        .order_by(Laboratorio.nome.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return labs


@router.get("/{laboratorio_id}", response_model=LaboratorioResponse)
def obter_laboratorio(
    laboratorio_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtém detalhes de um laboratório específico."""
    lab = db.query(Laboratorio).filter(Laboratorio.id == laboratorio_id).first()
    if not lab:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Laboratório não encontrado",
        )
    return lab


@router.post(
    "/",
    response_model=LaboratorioResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_laboratorio(
    laboratorio: LaboratorioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cria um novo laboratório acreditado."""
    new_id = uuid.uuid4().hex[:32]

    db_laboratorio = Laboratorio(
        id=new_id,
        **laboratorio.model_dump(),
    )
    db.add(db_laboratorio)
    db.commit()
    db.refresh(db_laboratorio)
    return db_laboratorio


@router.patch("/{laboratorio_id}", response_model=LaboratorioResponse)
def atualizar_laboratorio(
    laboratorio_id: str,
    laboratorio: LaboratorioUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Atualiza parcialmente os dados de um laboratório."""
    db_laboratorio = (
        db.query(Laboratorio).filter(Laboratorio.id == laboratorio_id).first()
    )
    if not db_laboratorio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Laboratório não encontrado",
        )

    update_data = laboratorio.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_laboratorio, field, value)

    db.commit()
    db.refresh(db_laboratorio)
    return db_laboratorio


@router.delete("/{laboratorio_id}", response_model=MessageResponse)
def deletar_laboratorio(
    laboratorio_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove um laboratório cadastrado."""
    db_laboratorio = (
        db.query(Laboratorio).filter(Laboratorio.id == laboratorio_id).first()
    )
    if not db_laboratorio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Laboratório não encontrado",
        )

    db.delete(db_laboratorio)
    db.commit()
    return MessageResponse(message="Laboratório removido com sucesso")

