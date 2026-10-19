from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.config.database import get_db
from app.models.auditoria_acesso import AuditoriaAcesso
from app.schemas.auditoria_acesso import AuditoriaAcessoResponse
from app.models.users import User
from app.utils.security import get_admin_user

router = APIRouter(prefix="/api/auditoria", tags=["Auditoria Técnica"])


@router.get("/acessos", response_model=List[AuditoriaAcessoResponse])
def listar_acessos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    """
    Lista registros de auditoria (visualizações de fotos, acessos a partes sensíveis, etc).
    Apenas administradores podem visualizar, garantindo a governança dos dados.
    """
    return (
        db.query(AuditoriaAcesso)
        .order_by(AuditoriaAcesso.data_hora.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
