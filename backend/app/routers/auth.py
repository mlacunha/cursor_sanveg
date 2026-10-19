from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from uuid import uuid4

from app.config.database import get_db
from app.config.settings import get_settings
from app.models.users import User
from app.schemas.auth import (
    LoginResponse,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    MessageResponse,
)
from app.schemas.user import UserLogin, UserLoginResponse
from app.utils.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    generate_reset_token,
    create_reset_token_expiry,
)
from app.utils.email import send_password_reset_email

router = APIRouter(prefix="/api/auth", tags=["Autenticação"])
settings = get_settings()


def _build_user_response(user: User) -> UserLoginResponse:
    return UserLoginResponse(
        id=user.id,
        login=user.login,
        nome=user.nome,
        email=user.email,
        cpf=user.cpf,
        telefone=user.telefone,
        matricula=user.matricula,
        carteirafiscal=user.carteirafiscal,
        active=user.active,
        role=user.role,
        id_orgao=user.id_orgao,
        id_unidade=user.id_unidade,
        id_cargo=user.id_cargo,
        id_formacao=user.id_formacao,
        criado_em=user.criado_em,
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Autenticação com e-mail e senha.
    Retorna JWT e dados do usuário.
    """
    user = db.query(User).filter(User.email == user_credentials.email).first()

    if not user or not user.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos",
        )

    if not verify_password(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta de usuário inativa",
        )

    if not settings.SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço temporariamente indisponível",
        )

    access_token = create_access_token(
        data={"sub": user.login},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=_build_user_response(user),
    )


@router.get("/me", response_model=UserLoginResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Retorna os dados do usuário autenticado."""
    return _build_user_response(current_user)


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Altera a senha do usuário autenticado."""
    if not verify_password(password_data.current_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta",
        )
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nova senha e confirmação não coincidem",
        )
    if password_data.current_password == password_data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A nova senha deve ser diferente da senha atual",
        )

    current_user.password = get_password_hash(password_data.new_password)
    current_user.atualizado_em = datetime.utcnow()
    db.commit()
    return MessageResponse(message="Senha alterada com sucesso")


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    """Solicita link de redefinição de senha por e-mail."""
    user = db.query(User).filter(User.email == request.email).first()

    if user:
        reset_token = generate_reset_token()
        user.reset_token = reset_token
        user.reset_token_expires = create_reset_token_expiry()
        db.commit()

        await send_password_reset_email(
            to_email=user.email,
            reset_token=reset_token,
            user_name=user.nome or "",
        )

    return MessageResponse(message="Se o e-mail existir, um link de redefinição foi enviado")


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    """Redefine a senha usando o token recebido por e-mail."""
    if request.new_password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senhas não coincidem",
        )

    user = db.query(User).filter(User.reset_token == request.token).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido ou expirado",
        )
    if user.reset_token_expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token expirado",
        )

    user.password = get_password_hash(request.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    user.atualizado_em = datetime.utcnow()
    db.commit()
    return MessageResponse(message="Senha redefinida com sucesso")
