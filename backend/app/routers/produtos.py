from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import uuid

from app.config.database import get_db
from app.models.produto import Produto
from app.schemas.produto import ProdutoCreate, ProdutoUpdate, ProdutoResponse
from app.schemas.common import MessageResponse
from app.utils.security import get_current_user
from app.models.users import User

router = APIRouter(
    prefix="/api/produtos",
    tags=["produtos"],
)


@router.get("/", response_model=List[ProdutoResponse])
def get_produtos(
    id_propriedade: Optional[str] = Query(None, description="Filtrar por propriedade"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Listar produtos."""
    query = db.query(Produto).options(joinedload(Produto.propriedade_data))
    if id_propriedade:
        query = query.filter(Produto.id_propriedade == id_propriedade)
    produtos = query.offset(skip).limit(limit).all()
    return produtos


@router.get("/{produto_id}", response_model=ProdutoResponse)
def get_produto(
    produto_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obter um produto pelo ID."""
    produto = (
        db.query(Produto)
        .options(joinedload(Produto.propriedade_data))
        .filter(Produto.id == produto_id)
        .first()
    )
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado",
        )
    return produto


@router.post("/", response_model=ProdutoResponse, status_code=status.HTTP_201_CREATED)
def create_produto(
    produto: ProdutoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Criar novo produto."""
    new_id = str(uuid.uuid4())
    db_produto = Produto(id=new_id, **produto.model_dump())
    db.add(db_produto)
    db.commit()
    db.refresh(db_produto, ["propriedade_data"])
    return db_produto


@router.patch("/{produto_id}", response_model=ProdutoResponse)
def update_produto(
    produto_id: str,
    produto: ProdutoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Atualizar produto (PATCH)."""
    db_produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not db_produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado",
        )
    update_data = produto.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_produto, field, value)
    db.commit()
    db.refresh(db_produto, ["propriedade_data"])
    return db_produto


@router.delete("/{produto_id}", response_model=MessageResponse)
def delete_produto(
    produto_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Deletar produto."""
    db_produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not db_produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado",
        )
    db.delete(db_produto)
    db.commit()
    return MessageResponse(message="Produto deletado com sucesso")
