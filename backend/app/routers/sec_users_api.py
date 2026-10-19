from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.config.database import get_db
from app.models.sec_user_api import SecUserApi as UserApi
from app.schemas.sec_user_api import (
    SecUserApiCreate as UserApiCreate,
    SecUserApiUpdate as UserApiUpdate,
    SecUserApiResponse as UserApiResponse,
)
from app.schemas.common import MessageResponse
from app.utils.security import get_current_user
from app.models.users import User

router = APIRouter(
    prefix="/api/sec-users-api",
    tags=["sec-users-api"],
)


@router.get("/", response_model=List[UserApiResponse])
def get_sec_users_api(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Listar usuários API. Senha não é retornada."""
    users = db.query(UserApi).offset(skip).limit(limit).all()
    return users


@router.get("/{login}", response_model=UserApiResponse)
def get_sec_user_api(
    login: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obter usuário API pelo login. Senha não é retornada."""
    user = db.query(UserApi).filter(UserApi.login == login).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário API não encontrado",
        )
    return user


@router.post("/", response_model=UserApiResponse, status_code=status.HTTP_201_CREATED)
def create_sec_user_api(
    user: UserApiCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Criar novo usuário API."""
    existing = db.query(UserApi).filter(UserApi.login == user.login).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Login já existente",
        )
    db_user = UserApi(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.patch("/{login}", response_model=UserApiResponse)
def update_sec_user_api(
    login: str,
    user: UserApiUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Atualizar usuário API (PATCH). Não é possível alterar login."""
    db_user = db.query(UserApi).filter(UserApi.login == login).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário API não encontrado",
        )
    update_data = user.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete("/{login}", response_model=MessageResponse)
def delete_sec_user_api(
    login: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Deletar usuário API."""
    db_user = db.query(UserApi).filter(UserApi.login == login).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário API não encontrado",
        )
    db.delete(db_user)
    db.commit()
    return MessageResponse(message="Usuário API deletado com sucesso")
