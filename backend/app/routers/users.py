from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from uuid import uuid4
from datetime import datetime

from app.config.database import get_db
from app.models.users import User
from app.schemas.users import UserCreate, UserUpdate, UserResponse
from app.schemas.common import MessageResponse
from app.utils.security import get_admin_user, get_password_hash

router = APIRouter(prefix="/api/users", tags=["Usuários"])


@router.get("/", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    """Lista todos os usuários. Apenas admins."""
    return (
        db.query(User)
        .options(
            joinedload(User.orgao_data),
            joinedload(User.unidade_data),
            joinedload(User.cargo_data),
            joinedload(User.formacao_data),
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{login}", response_model=UserResponse)
def get_user(
    login: str,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    """Retorna um usuário pelo login. Apenas admins."""
    user = (
        db.query(User)
        .options(
            joinedload(User.orgao_data),
            joinedload(User.unidade_data),
            joinedload(User.cargo_data),
            joinedload(User.formacao_data),
        )
        .filter(User.login == login)
        .first()
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    """Cria um novo usuário. Apenas admins."""
    if db.query(User).filter(User.login == user_in.login).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Login já existe")

    if user_in.email and db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-mail já cadastrado")

    data = user_in.model_dump()
    data["id"] = uuid4().hex
    data["password"] = get_password_hash(data["password"])

    db_user = User(**data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.patch("/{login}", response_model=UserResponse)
def update_user(
    login: str,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    """Atualiza parcialmente um usuário. Apenas admins."""
    db_user = db.query(User).filter(User.login == login).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    update_data = user_in.model_dump(exclude_unset=True)

    if "password" in update_data and update_data["password"]:
        update_data["password"] = get_password_hash(update_data["password"])

    if "email" in update_data and update_data["email"] and update_data["email"] != db_user.email:
        if db.query(User).filter(User.email == update_data["email"]).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-mail já cadastrado")

    for field, value in update_data.items():
        setattr(db_user, field, value)

    db_user.atualizado_em = datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete("/{login}", response_model=MessageResponse)
def delete_user(
    login: str,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    """Remove um usuário. Apenas admins. Não é possível remover a si mesmo."""
    db_user = db.query(User).filter(User.login == login).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    if db_user.login == admin_user.login:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você não pode remover seu próprio usuário",
        )

    db.delete(db_user)
    db.commit()
    return MessageResponse(message="Usuário removido com sucesso")
