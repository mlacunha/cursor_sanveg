from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
import uuid

from app.config.database import get_db
from app.models.hospedeiro import Hospedeiro
from app.schemas.hospedeiro import (
    HospedeiroCreate,
    HospedeiroUpdate,
    HospedeiroResponse
)
from app.schemas.common import MessageResponse
from app.utils.security import get_current_user
from app.models.users import User

router = APIRouter(
    prefix="/api/hospedeiros",
    tags=["hospedeiros"]
)


@router.get("/", response_model=List[HospedeiroResponse])
def get_hospedeiros(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all hospedeiros with optional programa data"""
    hospedeiros = db.query(Hospedeiro).options(
        joinedload(Hospedeiro.programa)
    ).offset(skip).limit(limit).all()
    return hospedeiros


@router.get("/{hospedeiro_id}", response_model=HospedeiroResponse)
def get_hospedeiro(
    hospedeiro_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific hospedeiro by ID with optional programa data"""
    hospedeiro = db.query(Hospedeiro).options(
        joinedload(Hospedeiro.programa)
    ).filter(Hospedeiro.id == hospedeiro_id).first()
    
    if not hospedeiro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospedeiro não encontrado"
        )
    
    return hospedeiro


@router.post("/", response_model=HospedeiroResponse, status_code=status.HTTP_201_CREATED)
def create_hospedeiro(
    hospedeiro: HospedeiroCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new hospedeiro"""
    # Generate UUID for the new hospedeiro
    new_id = str(uuid.uuid4())
    
    db_hospedeiro = Hospedeiro(
        id=new_id,
        **hospedeiro.model_dump()
    )
    
    db.add(db_hospedeiro)
    db.commit()
    db.refresh(db_hospedeiro, ['programa'])
    
    return db_hospedeiro


@router.patch("/{hospedeiro_id}", response_model=HospedeiroResponse)
def update_hospedeiro(
    hospedeiro_id: str,
    hospedeiro: HospedeiroUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a hospedeiro (partial update - only provided fields)"""
    db_hospedeiro = db.query(Hospedeiro).filter(
        Hospedeiro.id == hospedeiro_id
    ).first()
    
    if not db_hospedeiro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospedeiro não encontrado"
        )
    
    # Update only the fields that were provided
    update_data = hospedeiro.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_hospedeiro, field, value)
    
    db.commit()
    db.refresh(db_hospedeiro, ['programa'])
    
    return db_hospedeiro


@router.delete("/{hospedeiro_id}", response_model=MessageResponse)
def delete_hospedeiro(
    hospedeiro_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a hospedeiro"""
    db_hospedeiro = db.query(Hospedeiro).filter(
        Hospedeiro.id == hospedeiro_id
    ).first()
    
    if not db_hospedeiro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospedeiro não encontrado"
        )
    
    db.delete(db_hospedeiro)
    db.commit()
    
    return MessageResponse(message="Hospedeiro deletado com sucesso")
