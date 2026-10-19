from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import uuid

from app.config.database import get_db
from app.models.norma import Norma
from app.schemas.norma import (
    NormaCreate,
    NormaUpdate,
    NormaResponse
)
from app.schemas.common import MessageResponse
from app.utils.security import get_current_user
from app.models.users import User

router = APIRouter(
    prefix="/api/normas",
    tags=["normas"]
)


@router.get("/", response_model=List[NormaResponse])
def get_normas(
    id_programa: Optional[str] = Query(None, description="Filter by programa id"),
    nome_norma: Optional[str] = Query(None, description="Partial, case-insensitive match for norma name"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get normas with optional filters:

    - `id_programa`: filter normas belonging to a programa
    - `nome_norma`: partial, case-insensitive match against `nome_norma`

    Supports `skip` and `limit` for pagination.
    """
    query = db.query(Norma).options(joinedload(Norma.programa))

    if id_programa:
        query = query.filter(Norma.id_programa == id_programa)

    if nome_norma:
        pattern = f"%{nome_norma}%"
        query = query.filter(Norma.nome_norma.ilike(pattern))

    normas = query.offset(skip).limit(limit).all()
    return normas


@router.get("/{norma_id}", response_model=NormaResponse)
def get_norma(
    norma_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific norma by ID with optional programa data"""
    norma = db.query(Norma).options(
        joinedload(Norma.programa)
    ).filter(Norma.id == norma_id).first()
    
    if not norma:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Norma não encontrada"
        )
    
    return norma


@router.post("/", response_model=NormaResponse, status_code=status.HTTP_201_CREATED)
def create_norma(
    norma: NormaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new norma"""
    # Generate UUID for the new norma
    new_id = uuid.uuid4().hex[:18]
    
    db_norma = Norma(
        id=new_id,
        **norma.model_dump()
    )
    
    db.add(db_norma)
    db.commit()
    db.refresh(db_norma, ['programa'])
    
    return db_norma


@router.patch("/{norma_id}", response_model=NormaResponse)
def update_norma(
    norma_id: str,
    norma: NormaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a norma (partial update - only provided fields)"""
    db_norma = db.query(Norma).filter(
        Norma.id == norma_id
    ).first()
    
    if not db_norma:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Norma não encontrada"
        )
    
    # Update only the fields that were provided
    update_data = norma.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_norma, field, value)
    
    db.commit()
    db.refresh(db_norma, ['programa'])
    
    return db_norma


@router.delete("/{norma_id}", response_model=MessageResponse)
def delete_norma(
    norma_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a norma"""
    db_norma = db.query(Norma).filter(
        Norma.id == norma_id
    ).first()
    
    if not db_norma:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Norma não encontrada"
        )
    
    db.delete(db_norma)
    db.commit()
    
    return MessageResponse(message="Norma deletada com sucesso")
