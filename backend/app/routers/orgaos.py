from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.config.database import get_db
from app.models.orgao import Orgao
from app.models.users import User
from app.schemas.orgao import (
    OrgaoCreate,
    OrgaoUpdate,
    OrgaoResponse
)
from app.schemas.common import MessageResponse
from app.utils.security import get_current_user
import uuid

router = APIRouter(prefix="/api/orgaos", tags=["Órgãos"])


@router.get("/", response_model=List[OrgaoResponse])
async def list_orgaos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Listar todos os órgãos (requer autenticação).
    Retorna com dados do tipo de órgão quando disponível.
    """
    orgaos = db.query(Orgao).options(
        joinedload(Orgao.orgao_tipo_data)
    ).offset(skip).limit(limit).all()
    
    return orgaos


@router.get("/{orgao_id}", response_model=OrgaoResponse)
async def get_orgao(
    orgao_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obter um órgão específico por ID (requer autenticação).
    Retorna com dados do tipo de órgão quando disponível.
    """
    orgao = db.query(Orgao).options(
        joinedload(Orgao.orgao_tipo_data)
    ).filter(Orgao.id == orgao_id).first()
    
    if not orgao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Órgão não encontrado"
        )
    
    return orgao


@router.post("/", response_model=OrgaoResponse, status_code=status.HTTP_201_CREATED)
async def create_orgao(
    orgao_in: OrgaoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Criar novo órgão (requer autenticação).
    """
    # Gerar ID se não fornecido
    if not orgao_in.id:
        orgao_in.id = str(uuid.uuid4().hex[:18])
    
    # Verificar se ID já existe
    existing = db.query(Orgao).filter(Orgao.id == orgao_in.id).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID já existe"
        )
    
    # Criar novo registro
    orgao = Orgao(
        id=orgao_in.id,
        sigla=orgao_in.sigla,
        nome=orgao_in.nome,
        id_tipo_orgao=orgao_in.id_tipo_orgao,
        cnpj=orgao_in.cnpj,
        logo=orgao_in.logo or "",
        url_logo=orgao_in.url_logo or "",
        servidor_logo=orgao_in.servidor_logo or "",
        UF_sede=orgao_in.UF_sede or ""
    )
    
    db.add(orgao)
    db.commit()
    db.refresh(orgao)
    
    # Carregar relacionamento
    db.refresh(orgao, ['orgao_tipo_data'])
    
    return orgao


@router.patch("/{orgao_id}", response_model=OrgaoResponse)
async def update_orgao(
    orgao_id: str,
    orgao_in: OrgaoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Atualizar órgão parcialmente (PATCH - apenas campos fornecidos).
    Requer autenticação.
    """
    # Buscar registro
    orgao = db.query(Orgao).filter(Orgao.id == orgao_id).first()
    
    if not orgao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Órgão não encontrado"
        )
    
    # Atualizar apenas campos fornecidos
    update_data = orgao_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(orgao, field, value)
    
    db.commit()
    db.refresh(orgao)
    
    # Carregar relacionamento
    db.refresh(orgao, ['orgao_tipo_data'])
    
    return orgao


@router.delete("/{orgao_id}", response_model=MessageResponse)
async def delete_orgao(
    orgao_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deletar órgão (requer autenticação).
    """
    orgao = db.query(Orgao).filter(Orgao.id == orgao_id).first()
    
    if not orgao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Órgão não encontrado"
        )
    
    db.delete(orgao)
    db.commit()
    
    return MessageResponse(message="Órgão deletado com sucesso")
