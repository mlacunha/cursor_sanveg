from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.config.database import get_db
from app.models.formacao import Formacao
from app.schemas.formacao import FormacaoCreate, FormacaoUpdate, FormacaoResponse
from app.schemas.common import MessageResponse
from app.utils.security import get_current_user
from app.models.users import User

router = APIRouter(prefix="/api/formacoes", tags=["formacoes"])


@router.get("/", response_model=List[FormacaoResponse])
def get_formacoes(
    skip: int = 0,
    limit: int = 200,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Formacao).order_by(Formacao.nome).offset(skip).limit(limit).all()


@router.get("/{formacao_id}", response_model=FormacaoResponse)
def get_formacao(
    formacao_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    obj = db.query(Formacao).filter(Formacao.id == formacao_id).first()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Formação não encontrada")
    return obj


@router.post("/", response_model=FormacaoResponse, status_code=status.HTTP_201_CREATED)
def create_formacao(
    formacao_in: FormacaoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    obj = Formacao(
        id=formacao_in.id or str(uuid.uuid4()),
        nome=formacao_in.nome,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.patch("/{formacao_id}", response_model=FormacaoResponse)
def update_formacao(
    formacao_id: str,
    formacao_in: FormacaoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    obj = db.query(Formacao).filter(Formacao.id == formacao_id).first()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Formação não encontrada")

    for field, value in formacao_in.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)

    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{formacao_id}", response_model=MessageResponse)
def delete_formacao(
    formacao_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    obj = db.query(Formacao).filter(Formacao.id == formacao_id).first()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Formação não encontrada")

    db.delete(obj)
    db.commit()
    return MessageResponse(message="Formação excluída com sucesso")
