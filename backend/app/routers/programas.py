from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import uuid

from app.config.database import get_db
from app.models.programa import Programa
from app.schemas.programa import (
    ProgramaCreate,
    ProgramaUpdate,
    ProgramaResponse
)
from app.models.hospedeiro import Hospedeiro
from app.schemas.hospedeiro import HospedeiroResponse
from app.schemas.common import MessageResponse
from app.utils.security import get_current_user
from app.models.users import User

router = APIRouter(
    prefix="/api/programas",
    tags=["programas"]
)


@router.get("/", response_model=List[ProgramaResponse])
def get_programas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all programas"""
    programas = db.query(Programa).offset(skip).limit(limit).all()
    return programas


@router.get("/{programa_id}", response_model=ProgramaResponse)
def get_programa(
    programa_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific programa by ID"""
    programa = db.query(Programa).filter(
        Programa.id == programa_id
    ).first()
    
    if not programa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Programa não encontrado"
        )
    
    return programa


@router.post("/", response_model=ProgramaResponse, status_code=status.HTTP_201_CREATED)
def create_programa(
    programa: ProgramaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new programa"""
    # Generate UUID for the new programa
    new_id = uuid.uuid4().hex[:18]
    
    db_programa = Programa(
        id=new_id,
        **programa.model_dump()
    )
    
    db.add(db_programa)
    db.commit()
    db.refresh(db_programa)
    
    return db_programa


@router.patch("/{programa_id}", response_model=ProgramaResponse)
def update_programa(
    programa_id: str,
    programa: ProgramaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a programa (partial update - only provided fields)"""
    db_programa = db.query(Programa).filter(
        Programa.id == programa_id
    ).first()
    
    if not db_programa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Programa não encontrado"
        )
    
    # Update only the fields that were provided
    update_data = programa.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_programa, field, value)
    
    db.commit()
    db.refresh(db_programa)
    
    return db_programa


@router.delete("/{programa_id}", response_model=MessageResponse)
def delete_programa(
    programa_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a programa"""
    db_programa = db.query(Programa).filter(
        Programa.id == programa_id
    ).first()
    
    if not db_programa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Programa não encontrado"
        )
    
    db.delete(db_programa)
    db.commit()
    
    return MessageResponse(message="Programa deletado com sucesso")


@router.get("/{programa_id}/hospedeiros", response_model=List[HospedeiroResponse])
def get_hospedeiros_by_programa(
    programa_id: str,
    nome: Optional[str] = None,
    nome_cientifico: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get hospedeiros filtered by `id_programa` with optional name filters.

    - `nome`: partial case-insensitive match against `nomes_comuns`
    - `nome_cientifico`: partial case-insensitive match against
      `nome_cientifico`

    Supports `skip` and `limit` for pagination.
    """
    query = db.query(Hospedeiro).options(
        joinedload(Hospedeiro.programa)
    ).filter(Hospedeiro.id_programa == programa_id)

    if nome:
        pattern = f"%{nome}%"
        query = query.filter(Hospedeiro.nomes_comuns.ilike(pattern))

    if nome_cientifico:
        pattern_cf = f"%{nome_cientifico}%"
        query = query.filter(Hospedeiro.nome_cientifico.ilike(pattern_cf))

    hospedeiros = query.offset(skip).limit(limit).all()

    return hospedeiros
