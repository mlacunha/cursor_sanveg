from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.config.database import get_db
from app.models.produtor import Produtor
from app.schemas.produtor import (
    ProdutorCreate, ProdutorUpdate, ProdutorResponse
)
from app.utils.security import get_current_user
from app.services.locations import attach_location_info, attach_location_info_batch
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/api/produtores",
    tags=["produtores"]
)


@router.get("/", response_model=List[ProdutorResponse])
def get_produtores(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Listar todos os produtores"""
    produtores = db.query(Produtor).offset(skip).limit(limit).all()
    attach_location_info_batch(produtores, db)
    return produtores


@router.get("/{produtor_id}", response_model=ProdutorResponse)
def get_produtor(
    produtor_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Obter um produtor específico"""
    produtor = db.query(Produtor).filter(Produtor.id == produtor_id).first()
    if not produtor:
        raise HTTPException(status_code=404, detail="Produtor não encontrado")
    attach_location_info(produtor, db)
    return produtor


@router.post(
    "/",
    response_model=ProdutorResponse,
    status_code=status.HTTP_201_CREATED
)
def create_produtor(
    produtor: ProdutorCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Criar novo produtor"""
    # Gera ID único
    new_id = uuid.uuid4().hex[:18]
    
    db_produtor = Produtor(
        id=new_id,
        **produtor.model_dump()
    )
    
    db.add(db_produtor)
    db.commit()
    db.refresh(db_produtor)
    return db_produtor


@router.patch("/{produtor_id}", response_model=ProdutorResponse)
def update_produtor(
    produtor_id: str,
    produtor: ProdutorUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Atualizar um produtor (PATCH - apenas campos fornecidos)"""
    db_produtor = db.query(Produtor).filter(Produtor.id == produtor_id).first()
    if not db_produtor:
        raise HTTPException(status_code=404, detail="Produtor não encontrado")
    
    # Atualiza apenas os campos fornecidos
    update_data = produtor.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_produtor, field, value)
    
    db.commit()
    db.refresh(db_produtor)
    return db_produtor


@router.delete("/{produtor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_produtor(
    produtor_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Deletar um produtor"""
    db_produtor = db.query(Produtor).filter(Produtor.id == produtor_id).first()
    if not db_produtor:
        raise HTTPException(status_code=404, detail="Produtor não encontrado")
    
    db.delete(db_produtor)
    db.commit()
    return None
