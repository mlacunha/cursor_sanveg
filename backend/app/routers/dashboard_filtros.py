from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.config.database import get_db
from app.models.dashboard_filtros import DashboardFiltros
from app.schemas.dashboard_filtros import (
    DashboardFiltrosCreate,
    DashboardFiltrosUpdate,
    DashboardFiltrosResponse,
)
from app.schemas.common import MessageResponse
from app.utils.security import get_current_user
from app.models.users import User

router = APIRouter(
    prefix="/api/dashboard-filtros",
    tags=["dashboard-filtros"],
)


@router.get("/", response_model=List[DashboardFiltrosResponse])
def get_dashboard_filtros(
    id_programa: Optional[str] = Query(None, description="Filtrar por programa"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Listar filtros do dashboard."""
    query = db.query(DashboardFiltros)
    if id_programa:
        query = query.filter(DashboardFiltros.id_programa == id_programa)
    filtros = query.offset(skip).limit(limit).all()
    return filtros


@router.get("/{filtro_id}", response_model=DashboardFiltrosResponse)
def get_dashboard_filtro(
    filtro_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obter filtro do dashboard pelo ID."""
    filtro = db.query(DashboardFiltros).filter(DashboardFiltros.id == filtro_id).first()
    if not filtro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Filtro do dashboard não encontrado",
        )
    return filtro


@router.post(
    "/",
    response_model=DashboardFiltrosResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_dashboard_filtro(
    filtro: DashboardFiltrosCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Criar novo filtro do dashboard."""
    db_filtro = DashboardFiltros(**filtro.model_dump())
    db.add(db_filtro)
    db.commit()
    db.refresh(db_filtro)
    return db_filtro


@router.patch("/{filtro_id}", response_model=DashboardFiltrosResponse)
def update_dashboard_filtro(
    filtro_id: int,
    filtro: DashboardFiltrosUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Atualizar filtro do dashboard (PATCH)."""
    db_filtro = db.query(DashboardFiltros).filter(DashboardFiltros.id == filtro_id).first()
    if not db_filtro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Filtro do dashboard não encontrado",
        )
    update_data = filtro.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_filtro, field, value)
    db.commit()
    db.refresh(db_filtro)
    return db_filtro


@router.delete("/{filtro_id}", response_model=MessageResponse)
def delete_dashboard_filtro(
    filtro_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Deletar filtro do dashboard."""
    db_filtro = db.query(DashboardFiltros).filter(DashboardFiltros.id == filtro_id).first()
    if not db_filtro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Filtro do dashboard não encontrado",
        )
    db.delete(db_filtro)
    db.commit()
    return MessageResponse(message="Filtro do dashboard deletado com sucesso")
