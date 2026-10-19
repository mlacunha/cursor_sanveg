from fastapi import APIRouter, Depends, Query, HTTPException
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional

from app.config.database import get_db
from app.utils.security import get_current_user
from app.models.users import User
from app.schemas.relatorio_resumo import RelatorioResumoSummary

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/relatorios/resumo",
    tags=["relatorios"]
)

@router.get("/", response_model=RelatorioResumoSummary)
def get_relatorio_resumo(
    id_programa: Optional[str] = Query(None, description="Programa id to filter by"),
    ano: Optional[str] = Query(None, description="Year (YYYY)"),
    trimestre: Optional[int] = Query(None, description="Trimestre (1-4)"),
    municipio: Optional[str] = Query(None, description="Municipio name"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Return summarized totals from vw_relatorio_totais (all filters optional).

    Uses COUNT(DISTINCT id_programa), COUNT(*), COUNT(DISTINCT municipio) and
    conditional SUMs for statuses SUSPEITA and FOCO as integers.
    """

    sql_template = (
        """
        SELECT
            COUNT(DISTINCT T1.id_programa) AS total_programas,
            COUNT(*) AS total_inspecoes,
            COUNT(DISTINCT T1.municipio) AS total_municipios,
            COALESCE(SUM(CASE WHEN T1.status = 'SUSPEITA' THEN 1 ELSE 0 END),0) AS total_suspeitas,
            COALESCE(SUM(CASE WHEN T1.status = 'FOCO' THEN 1 ELSE 0 END),0) AS total_focos
        FROM {table} T1
        WHERE (:id_programa IS NULL OR T1.id_programa = :id_programa)
          AND (:ano IS NULL OR T1.ano = :ano)
          AND (:trimestre IS NULL OR T1.trimestre = :trimestre)
          AND (:municipio IS NULL OR T1.municipio = :municipio)
        """
    )

    params = {
        "id_programa": id_programa,
        "ano": ano,
        "trimestre": trimestre,
        "municipio": municipio,
    }

    # Prefer the view 'vw_relatorio_resumo' (exists in this DB). If it fails,
    # fall back to the physical table 'relatorio_mapa'. This avoids trying
    # views that do not exist in the target schema.
    res = None
    try:
        table_used = 'vw_relatorio_resumo'
        logger.info('Attempting summary query on %s', table_used)
        sql = text(sql_template.format(table=table_used))
        res = db.execute(sql, params).mappings().first()
        logger.info('Summary query on %s executed', table_used)
    except Exception:
        try:
            table_used = 'relatorio_mapa'
            logger.warning('vw_relatorio_resumo failed, falling back to %s', table_used)
            sql = text(sql_template.format(table=table_used))
            res = db.execute(sql, params).mappings().first()
            logger.info('Summary query on %s executed', table_used)
        except Exception as e:
            logger.exception('Summary query failed for both vw_relatorio_resumo and relatorio_mapa')
            raise HTTPException(status_code=500, detail=f"Database query failed: {e}")

    if not res:
        # Return zeros for all numeric fields (suitable for dashboards)
        return RelatorioResumoSummary(
            total_programas=0,
            total_inspecoes=0,
            total_municipios=0,
            total_suspeitas=0,
            total_focos=0,
        )

    # map values and ensure numeric types (always integers for dashboard)
    def to_int(v):
        try:
            if v is None:
                return 0
            return int(v)
        except Exception:
            try:
                # handle Decimal-like objects
                return int(float(v))
            except Exception:
                return 0

    return RelatorioResumoSummary(
        total_programas=to_int(res.get('total_programas')),
        total_inspecoes=to_int(res.get('total_inspecoes')),
        total_municipios=to_int(res.get('total_municipios')),
        total_suspeitas=to_int(res.get('total_suspeitas')),
        total_focos=to_int(res.get('total_focos')),
    )
