from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.estado import Estado
from app.schemas.estado import EstadoResponse
from app.utils.security import get_admin_user
from app.services.estados_import import import_estados

router = APIRouter(prefix="/api/estados", tags=["Auxiliares"])


@router.get("/", response_model=List[EstadoResponse])
async def list_estados(
    db: Session = Depends(get_db),
):
    return db.query(Estado).order_by(Estado.sigla.asc(), Estado.nome.asc()).all()


@router.get("/{estado_id}", response_model=EstadoResponse)
async def get_estado(estado_id: int, db: Session = Depends(get_db)):
    estado = db.query(Estado).filter(Estado.id == estado_id).first()
    if not estado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estado não encontrado")
    return estado



@router.post("/import", status_code=202)
async def import_estados_route(
    sync: bool = False,
    background_tasks: BackgroundTasks = None,
    current_admin = Depends(get_admin_user),
):
    """Dispara a importação dos estados via IBGE.

    - `sync=true` executa sincronamente e retorna o resultado.
    - sem `sync` a importação é executada em background e retorna 202.
    Rota protegida, requer usuário admin.
    """
    if sync:
        results = import_estados()
        return {"status": "completed", "results": results}

    if background_tasks is not None:
        background_tasks.add_task(import_estados)
        return {"status": "started", "message": "Import started in background"}

    # fallback sync
    results = import_estados()
    return {"status": "completed", "results": results}
