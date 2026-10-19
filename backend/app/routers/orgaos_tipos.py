from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.config.database import get_db
from app.models.orgao_tipo import OrgaoTipo
from app.models.users import User
from app.schemas.orgao_tipo import (
    OrgaoTipoCreate,
    OrgaoTipoUpdate,
    OrgaoTipoResponse
)
from app.schemas.common import MessageResponse
from app.utils.security import get_current_user
import uuid

router = APIRouter(prefix="/api/orgaos-tipos", tags=["Órgãos Tipos"])


@router.get("/", response_model=List[OrgaoTipoResponse])
async def list_orgaos_tipos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Listar todos os tipos de órgãos (requer autenticação).
    """
    orgaos_tipos = db.query(OrgaoTipo).offset(skip).limit(limit).all()
    return orgaos_tipos


@router.get("/{orgao_tipo_id}", response_model=OrgaoTipoResponse)
async def get_orgao_tipo(
    orgao_tipo_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obter um tipo de órgão específico por ID (requer autenticação).
    """
    orgao_tipo = db.query(OrgaoTipo).filter(
        OrgaoTipo.id == orgao_tipo_id
    ).first()
    
    if not orgao_tipo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipo de órgão não encontrado"
        )
    
    return orgao_tipo


@router.post("/", response_model=OrgaoTipoResponse, status_code=status.HTTP_201_CREATED)
async def create_orgao_tipo(
    orgao_tipo_in: OrgaoTipoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Criar novo tipo de órgão (requer autenticação).
    """
    # Gerar ID se não fornecido
    if not orgao_tipo_in.id:
        orgao_tipo_in.id = str(uuid.uuid4().hex[:18])
    
    # Verificar se ID já existe
    existing = db.query(OrgaoTipo).filter(
        OrgaoTipo.id == orgao_tipo_in.id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID já existe"
        )
    
    # Criar novo registro
    orgao_tipo = OrgaoTipo(
        id=orgao_tipo_in.id,
        nome=orgao_tipo_in.nome,
        descricao=orgao_tipo_in.descricao
    )
    
    db.add(orgao_tipo)
    db.commit()
    db.refresh(orgao_tipo)
    
    return orgao_tipo


@router.patch("/{orgao_tipo_id}", response_model=OrgaoTipoResponse)
async def update_orgao_tipo(
    orgao_tipo_id: str,
    orgao_tipo_in: OrgaoTipoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Atualizar tipo de órgão parcialmente (PATCH - apenas campos fornecidos).
    Requer autenticação.
    """
    # Buscar registro
    orgao_tipo = db.query(OrgaoTipo).filter(
        OrgaoTipo.id == orgao_tipo_id
    ).first()
    
    if not orgao_tipo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipo de órgão não encontrado"
        )
    
    # Atualizar apenas campos fornecidos
    update_data = orgao_tipo_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(orgao_tipo, field, value)
    
    db.commit()
    db.refresh(orgao_tipo)
    
    return orgao_tipo


@router.delete("/{orgao_tipo_id}", response_model=MessageResponse)
async def delete_orgao_tipo(
    orgao_tipo_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deletar tipo de órgão (requer autenticação).
    """
    orgao_tipo = db.query(OrgaoTipo).filter(
        OrgaoTipo.id == orgao_tipo_id
    ).first()
    
    if not orgao_tipo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipo de órgão não encontrado"
        )
    
    db.delete(orgao_tipo)
    db.commit()
    
    return MessageResponse(message="Tipo de órgão deletado com sucesso")
