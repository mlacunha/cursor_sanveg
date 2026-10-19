"""Serviços para importar municípios do IBGE.
Fornece funções reutilizáveis pelo CLI e pela API.
"""
from typing import Optional, Dict
import logging
import requests
from app.config.database import SessionLocal
from app.models.estado import Estado
from app.models.municipio import Municipio

IBGE_URL_TEMPLATE = (
    "https://servicodados.ibge.gov.br/api/v1/localidades/"
    "estados/{sigla}/municipios"
)


def fetch_municipios_of_estado(sigla: str):
    url = IBGE_URL_TEMPLATE.format(sigla=sigla)
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()


logger = logging.getLogger(__name__)


def import_for_estado(db, estado: Estado, force_reload: bool = False):
    """Importa municípios de um estado usando 1 query para existentes.

    Retorna: (total, existing_count, new_count)
    """
    municipios = fetch_municipios_of_estado(estado.sigla)
    ids = [m["id"] for m in municipios]

    existing_by_id = {}
    if ids:
        existing_list = db.query(Municipio).filter(Municipio.id.in_(ids)).all()
        existing_by_id = {o.id: o for o in existing_list}

    new_objs = []
    for m in municipios:
        mid = m["id"]
        if mid in existing_by_id:
            obj = existing_by_id[mid]
            obj.nome = m["nome"]
            obj.estado_id = estado.id
        else:
            new_objs.append(
                Municipio(id=mid, nome=m["nome"], estado_id=estado.id)
            )

    if new_objs:
        db.add_all(new_objs)

    total = len(municipios)
    existing_count = len(existing_by_id)
    new_count = len(new_objs)

    logger.debug(
        "Imported/updated %s municipios for estado %s (%s existing, %s new)",
        total,
        estado.sigla,
        existing_count,
        new_count,
    )

    return total, existing_count, new_count


def import_municipios(
    estado_sigla: Optional[str] = None,
    force_reload: bool = False,
    job_id: Optional[int] = None,
) -> Dict[str, int]:
    """Importa municípios para todos os estados ou para a sigla informada.

    Se `job_id` for fornecido, atualiza o registro do job; caso
    contrário, cria um novo job.

    Retorna dicionário {sigla: count, "total": total}
    """
    from app.models.import_job import ImportJob
    from datetime import datetime

    db = SessionLocal()
    try:
        # Prepare or fetch job record
        if job_id is None:
            job = ImportJob(
                estado_sigla=estado_sigla,
                status="running",
                force_reload=force_reload,
            )
            db.add(job)
            db.commit()
            db.refresh(job)
            job_id = job.id
        else:
            job = db.query(ImportJob).get(job_id)
            job.started_at = datetime.utcnow()
            job.status = "running"
            db.commit()

        estados_q = db.query(Estado)
        if estado_sigla:
            estados_q = estados_q.filter(Estado.sigla == estado_sigla.upper())

        estados = estados_q.all()
        total = 0
        results = {}
        accum_existing = 0
        accum_new = 0
        for e in estados:
            cnt, existing_count, new_count = import_for_estado(
                db, e, force_reload=force_reload
            )
            total += cnt
            accum_existing += existing_count
            accum_new += new_count
            db.commit()
            results[e.sigla] = cnt

            # update job progress after each state
            job.total = total
            job.existing = (job.existing or 0) + existing_count
            job.new = (job.new or 0) + new_count
            db.commit()

        job.status = "completed"
        job.finished_at = datetime.utcnow()
        job.total = total
        db.commit()

        results["total"] = total
        return results
    except Exception as exc:
        # update job as failed and re-raise
        try:
            job.status = "failed"
            job.error = str(exc)
            job.finished_at = datetime.utcnow()
            db.commit()
        except Exception:
            db.rollback()
        raise
    finally:
        db.close()
