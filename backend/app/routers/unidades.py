from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import uuid

from app.config.database import get_db
from app.models.unidade import Unidade
from app.schemas.unidade import UnidadeCreate, UnidadeUpdate, UnidadeResponse
from app.schemas.common import MessageResponse
from app.utils.security import get_current_user
from app.models.users import User

router = APIRouter(prefix="/api/unidades", tags=["unidades"])


@router.get("/", response_model=List[UnidadeResponse])
def get_unidades(
    id_orgao: Optional[str] = Query(None, description="Filtrar unidades por órgão"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Unidade).options(joinedload(Unidade.orgao_data))

    if id_orgao:
        query = query.filter(Unidade.id_orgao == id_orgao)

    return query.offset(skip).limit(limit).all()


@router.get("/{unidade_id}", response_model=UnidadeResponse)
def get_unidade(
    unidade_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    unidade = db.query(Unidade).options(
        joinedload(Unidade.orgao_data)
    ).filter(Unidade.id == unidade_id).first()

    if not unidade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unidade não encontrada")

    return unidade


@router.post("/", response_model=UnidadeResponse, status_code=status.HTTP_201_CREATED)
def create_unidade(
    unidade_in: UnidadeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_id = unidade_in.id or str(uuid.uuid4())

    db_unidade = Unidade(
        id=new_id,
        id_orgao=unidade_in.id_orgao,
        nome=unidade_in.nome,
        municipio=unidade_in.municipio,
        uf=unidade_in.uf,
    )

    db.add(db_unidade)
    db.commit()
    db.refresh(db_unidade, ['orgao_data'])
    return db_unidade


@router.patch("/{unidade_id}", response_model=UnidadeResponse)
def update_unidade(
    unidade_id: str,
    unidade_in: UnidadeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_unidade = db.query(Unidade).filter(Unidade.id == unidade_id).first()

    if not db_unidade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unidade não encontrada")

    for field, value in unidade_in.model_dump(exclude_unset=True).items():
        setattr(db_unidade, field, value)

    db.commit()
    db.refresh(db_unidade, ['orgao_data'])
    return db_unidade


@router.delete("/{unidade_id}", response_model=MessageResponse)
def delete_unidade(
    unidade_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_unidade = db.query(Unidade).filter(Unidade.id == unidade_id).first()

    if not db_unidade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unidade não encontrada")

    db.delete(db_unidade)
    db.commit()
    return MessageResponse(message="Unidade deletada com sucesso")
