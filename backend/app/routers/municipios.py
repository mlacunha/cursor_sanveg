from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from typing import List, Optional
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.municipio import Municipio
from app.schemas.municipio import MunicipioResponse
from app.utils.security import get_admin_user
from app.services.municipios_import import import_municipios
from app.schemas.import_job import ImportJobResponse


router = APIRouter(prefix="/api/municipios", tags=["Auxiliares"])


@router.get("/", response_model=List[MunicipioResponse])
async def list_municipios(
    uf_id: int = Query(..., description="ID da UF para filtrar os municipios."),
    db: Session = Depends(get_db),
):
    return (
        db.query(Municipio)
        .filter(Municipio.estado_id == uf_id)
        .order_by(Municipio.nome.asc())
        .all()
    )


@router.get("/{municipio_id}", response_model=MunicipioResponse)
async def get_municipio(municipio_id: int, db: Session = Depends(get_db)):
    municipio = db.query(Municipio).filter(
        Municipio.id == municipio_id
    ).first()
    if not municipio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Município não encontrado",
        )
    return municipio


@router.post("/import", status_code=202)
async def import_municipios_route(
    estado: Optional[str] = None,
    sync: bool = False,
    force_reload: bool = False,
    background_tasks: BackgroundTasks = None,
    current_admin=Depends(get_admin_user),
):
    """Dispara a importação de municípios.

    - `estado` (opcional): sigla do estado (ex: PA). Se omitido, importa todos.
    - `sync` (opcional): se True, roda a importação de forma síncrona
      e retorna o resultado.
    - `force_reload` (opcional): força recarga de dados (marcado no job).

    A rota é protegida e requer usuário admin (`priv_admin = 'Y'`).
    """
    # Síncrono: executa e retorna resultados
    if sync:
        results = import_municipios(estado, force_reload=force_reload)
        # try to get latest job id if created
        return {"status": "completed", "results": results}

    # Executa em background e retorna imediatamente com job id
    from app.models.import_job import ImportJob
    from app.config.database import SessionLocal

    db = SessionLocal()
    try:
        job = ImportJob(
            estado_sigla=estado, status="queued", force_reload=force_reload
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        job_id = job.id
    finally:
        db.close()

    if background_tasks is not None:
        # schedule a background task to run the import and update job
        background_tasks.add_task(
            import_municipios, estado, force_reload, job_id
        )
        return {"status": "started", "job_id": job_id}

    # Fallback (não esperado) — execute synchronously
    results = import_municipios(estado, force_reload=force_reload)
    return {"status": "completed", "results": results}


@router.get("/import/{job_id}", response_model=ImportJobResponse)
async def import_job_status(
    job_id: int,
    current_admin=Depends(get_admin_user),
):
    from app.config.database import SessionLocal
    from app.models.import_job import ImportJob

    db = SessionLocal()
    try:
        job = db.query(ImportJob).filter(
            ImportJob.id == job_id
        ).first()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found",
            )
        return job
    finally:
        db.close()


@router.get("/import/last", response_model=ImportJobResponse)
async def import_job_last(current_admin=Depends(get_admin_user)):
    from app.config.database import SessionLocal
    from app.models.import_job import ImportJob

    db = SessionLocal()
    try:
        job = db.query(ImportJob).order_by(
            ImportJob.created_at.desc()
        ).first()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No import jobs found",
            )
        return job
    finally:
        db.close()
