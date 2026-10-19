from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
import uuid

from app.config.database import get_db
from app.models.termo_inspecao import TermoInspecao
from app.models.controle_sequencial import ControleSequencial
from app.models.users import User
from app.schemas.termo_inspecao import (
    TermoInspecaoCreate, TermoInspecaoUpdate, TermoInspecaoResponse
)
from app.utils.security import get_current_user

router = APIRouter(
    prefix="/api/termo-inspecao",
    tags=["termo-inspecao"]
)


@router.get("/", response_model=List[TermoInspecaoResponse])
def get_termos_inspecao(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar todos os termos de inspeção com dados relacionados"""
    termos = db.query(TermoInspecao).options(
        joinedload(TermoInspecao.usuario_data),
        joinedload(TermoInspecao.propriedade_data)
    ).offset(skip).limit(limit).all()
    return termos


@router.get("/{termo_id}", response_model=TermoInspecaoResponse)
def get_termo_inspecao(
    termo_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obter um termo de inspeção específico com dados relacionados"""
    termo = db.query(TermoInspecao).options(
        joinedload(TermoInspecao.usuario_data),
        joinedload(TermoInspecao.propriedade_data)
    ).filter(TermoInspecao.id == termo_id).first()
    
    if not termo:
        raise HTTPException(
            status_code=404,
            detail="Termo de inspeção não encontrado"
        )
    return termo


@router.post(
    "/",
    response_model=TermoInspecaoResponse,
    status_code=status.HTTP_201_CREATED
)
def create_termo_inspecao(
    termo: TermoInspecaoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Criar novo termo de inspeção com geração automática de ficha_inspecao
    
    Lógica de geração de ficha_inspecao:
    1. Buscar usuário pelo id_usuario para obter o login
    2. Extrair o ano (YYYY) do campo data
    3. Verificar se existe registro em controle_sequencial com login + ano
    4. Se não existir, criar com seq_ti = 1
    5. Se existir, incrementar seq_ti em 1
    6. Usar o valor de seq_ti como ficha_inspecao
    """
    # Validar se usuário existe (id_usuario é o login)
    usuario = db.query(User).filter(
        User.login == termo.id_usuario
    ).first()
    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado"
        )
    
    # Extrair ano da data
    ano = termo.data.strftime("%Y")
    
    # Buscar ou criar registro de controle sequencial
    controle = db.query(ControleSequencial).filter(
        ControleSequencial.login == usuario.login,
        ControleSequencial.ano == ano
    ).first()
    
    if controle:
        # Incrementar seq_ti
        controle.seq_ti += 1
        ficha_numero = controle.seq_ti
    else:
        # Criar novo registro com seq_ti e seq_tc em 0
        controle = ControleSequencial(
            login=usuario.login,
            ano=ano,
            seq_ti=0,
            seq_tc=0
        )
        db.add(controle)
        # Incrementar para o primeiro termo
        controle.seq_ti += 1
        ficha_numero = controle.seq_ti
    
    # Gera ID único
    new_id = uuid.uuid4().hex[:18]
    
    # Criar termo de inspeção
    db_termo = TermoInspecao(
        id=new_id,
        data=termo.data,
        ficha_inspecao=ficha_numero,
        id_usuario=termo.id_usuario,
        id_propriedade=termo.id_propriedade
    )
    
    db.add(db_termo)
    db.commit()
    db.refresh(db_termo, ["usuario_data", "propriedade_data"])
    
    return db_termo


@router.patch("/{termo_id}", response_model=TermoInspecaoResponse)
def update_termo_inspecao(
    termo_id: str,
    termo: TermoInspecaoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualizar um termo de inspeção (PATCH - apenas campos fornecidos)"""
    db_termo = db.query(TermoInspecao).filter(
        TermoInspecao.id == termo_id
    ).first()
    
    if not db_termo:
        raise HTTPException(
            status_code=404,
            detail="Termo de inspeção não encontrado"
        )
    
    # Atualiza apenas os campos fornecidos
    update_data = termo.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_termo, field, value)
    
    db.commit()
    db.refresh(db_termo, ["usuario_data", "propriedade_data"])
    return db_termo


@router.delete("/{termo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_termo_inspecao(
    termo_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deletar um termo de inspeção"""
    db_termo = db.query(TermoInspecao).filter(
        TermoInspecao.id == termo_id
    ).first()
    
    if not db_termo:
        raise HTTPException(
            status_code=404,
            detail="Termo de inspeção não encontrado"
        )
    
    db.delete(db_termo)
    db.commit()
    return None
