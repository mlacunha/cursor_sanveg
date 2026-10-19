from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.config.database import get_db
from app.models.sec_setting import SecSetting
from app.schemas.sec_setting import (
    SecSettingCreate,
    SecSettingUpdate,
    SecSettingResponse,
)
from app.schemas.common import MessageResponse
from app.utils.security import get_current_user
from app.models.users import User

router = APIRouter(
    prefix="/api/sec-settings",
    tags=["sec-settings"],
)


@router.get("/", response_model=List[SecSettingResponse])
def get_sec_settings(
    skip: int = 0,
    limit: int = 200,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Listar configurações do sistema."""
    settings = db.query(SecSetting).offset(skip).limit(limit).all()
    return settings


@router.get("/{set_name}", response_model=SecSettingResponse)
def get_sec_setting(
    set_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obter configuração pelo nome."""
    setting = db.query(SecSetting).filter(SecSetting.set_name == set_name).first()
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuração não encontrada",
        )
    return setting


@router.post("/", response_model=SecSettingResponse, status_code=status.HTTP_201_CREATED)
def create_sec_setting(
    setting: SecSettingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Criar nova configuração."""
    existing = db.query(SecSetting).filter(SecSetting.set_name == setting.set_name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nome de configuração já existente",
        )
    db_setting = SecSetting(**setting.model_dump())
    db.add(db_setting)
    db.commit()
    db.refresh(db_setting)
    return db_setting


@router.patch("/{set_name}", response_model=SecSettingResponse)
def update_sec_setting(
    set_name: str,
    setting: SecSettingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Atualizar configuração (PATCH)."""
    db_setting = db.query(SecSetting).filter(SecSetting.set_name == set_name).first()
    if not db_setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuração não encontrada",
        )
    update_data = setting.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_setting, field, value)
    db.commit()
    db.refresh(db_setting)
    return db_setting


@router.delete("/{set_name}", response_model=MessageResponse)
def delete_sec_setting(
    set_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Deletar configuração."""
    db_setting = db.query(SecSetting).filter(SecSetting.set_name == set_name).first()
    if not db_setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuração não encontrada",
        )
    db.delete(db_setting)
    db.commit()
    return MessageResponse(message="Configuração deletada com sucesso")
