"""
Router: /api/relatorios/levantamentos

Serve o histórico unificado de levantamentos fitossanitários a partir da
VIEW vw_levantamentos, que combina:
  - dados legados (relatorio_mapa)
  - dados de inspeção via aplicativo (area_programa → area_inspecionada → termo_inspecao)

Filtros suportados: programa (nome), ano, trimestre, municipio, status
Resultado: lista paginada + opções de filtro (filter_options)

Colunas retornadas (em ordem):
  nome_programa | ano | trimestre | municipio | nome_propriedade |
  tipo_imovel   | cultura | latitude | longitude | status | data | fonte
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional

from app.config.database import get_db
from app.utils.security import get_current_user
from app.models.users import User

router = APIRouter(
    prefix="/api/relatorios",
    tags=["relatorios"],
)


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _build_where(
    programa: Optional[str],
    ano: Optional[str],
    trimestre: Optional[int],
    municipio: Optional[str],
    status: Optional[str],
) -> tuple[str, dict]:
    """Monta cláusula WHERE e parâmetros para queries na vw_levantamentos."""
    conditions = []
    params: dict = {}

    if programa:
        conditions.append("nome_programa LIKE :programa")
        params["programa"] = f"%{programa}%"

    if ano:
        conditions.append("ano = :ano")
        params["ano"] = str(ano)

    if trimestre:
        conditions.append("trimestre = :trimestre")
        params["trimestre"] = trimestre

    if municipio:
        conditions.append("municipio LIKE :municipio")
        params["municipio"] = f"%{municipio}%"

    if status:
        conditions.append("status = :status")
        params["status"] = status.upper()

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    return where, params


# ─── Endpoint principal ───────────────────────────────────────────────────────

@router.get("/levantamentos")
def get_levantamentos(
    programa: Optional[str]  = Query(None, description="Filtrar por nome do programa (parcial)"),
    ano:      Optional[str]  = Query(None, description="Filtrar por ano (YYYY)"),
    trimestre: Optional[int] = Query(None, description="Filtrar por trimestre (1-4)", ge=1, le=4),
    municipio: Optional[str] = Query(None, description="Filtrar por município (parcial)"),
    status:   Optional[str]  = Query(None, description="Filtrar por resultado: NORMAL | SUSPEITA | POSITIVO | FOCO"),
    page:     int            = Query(1, ge=1, description="Página (1-based)"),
    per_page: int            = Query(50, ge=1, le=500, description="Registros por página"),
    db:       Session        = Depends(get_db),
    current_user: User       = Depends(get_current_user),
):
    """
    Retorna o histórico consolidado de levantamentos fitossanitários.

    Combina dados legados (relatorio_mapa) e dados de inspeção via aplicativo
    através da VIEW vw_levantamentos.

    Resposta:
    ```json
    {
      "total": 500,
      "page": 1,
      "per_page": 50,
      "items": [ { nome_programa, ano, trimestre, municipio, nome_propriedade,
                   tipo_imovel, cultura, latitude, longitude, status, data, fonte } ],
      "filter_options": {
        "programas":  ["HLB", "Cancro Cítrico"],
        "anos":       ["2024", "2025", "2026"],
        "trimestres": ["1", "2", "3", "4"],
        "municipios": ["Belém", "Prainha"],
        "statuses":   ["NORMAL", "SUSPEITA", "POSITIVO", "FOCO"]
      }
    }
    ```
    """
    where, params = _build_where(programa, ano, trimestre, municipio, status)

    # ── Contagem total ────────────────────────────────────────────────────────
    count_sql = text(f"SELECT COUNT(*) FROM vw_levantamentos {where}")
    total: int = db.execute(count_sql, params).scalar() or 0

    # ── Dados paginados ───────────────────────────────────────────────────────
    offset = (page - 1) * per_page
    data_params = {**params, "limit": per_page, "offset": offset}

    data_sql = text(f"""
        SELECT
            nome_programa,
            ano,
            trimestre,
            municipio,
            nome_propriedade,
            tipo_imovel,
            cultura,
            CAST(latitude  AS DECIMAL(10,8)) AS latitude,
            CAST(longitude AS DECIMAL(11,8)) AS longitude,
            status,
            data,
            fonte
        FROM vw_levantamentos
        {where}
        ORDER BY nome_programa ASC, ano DESC, trimestre DESC, municipio ASC
        LIMIT :limit OFFSET :offset
    """)

    rows = db.execute(data_sql, data_params).mappings().all()

    items = [
        {
            "nome_programa":   r["nome_programa"],
            "ano":             r["ano"],
            "trimestre":       r["trimestre"],
            "municipio":       r["municipio"],
            "nome_propriedade": r["nome_propriedade"],
            "tipo_imovel":     r["tipo_imovel"],
            "cultura":         r["cultura"],
            "latitude":        float(r["latitude"])  if r["latitude"]  is not None else None,
            "longitude":       float(r["longitude"]) if r["longitude"] is not None else None,
            "status":          r["status"],
            "data":            str(r["data"]) if r["data"] else None,
            "fonte":           r["fonte"],
        }
        for r in rows
    ]

    # ── Opções de filtro (sem filtros aplicados → valores disponíveis no total) ─
    opts_sql = text("""
        SELECT
            GROUP_CONCAT(DISTINCT nome_programa ORDER BY nome_programa SEPARATOR '|') AS programas,
            GROUP_CONCAT(DISTINCT ano            ORDER BY ano DESC       SEPARATOR '|') AS anos,
            GROUP_CONCAT(DISTINCT trimestre      ORDER BY trimestre      SEPARATOR '|') AS trimestres,
            GROUP_CONCAT(DISTINCT municipio      ORDER BY municipio      SEPARATOR '|') AS municipios,
            GROUP_CONCAT(DISTINCT status         ORDER BY status         SEPARATOR '|') AS statuses
        FROM vw_levantamentos
        WHERE nome_programa IS NOT NULL
    """)

    opts_row = db.execute(opts_sql).mappings().one_or_none()

    def _split(val: Optional[str]) -> list[str]:
        return [v for v in (val or "").split("|") if v] if val else []

    filter_options = {
        "programas":  _split(opts_row["programas"])  if opts_row else [],
        "anos":       _split(opts_row["anos"])        if opts_row else [],
        "trimestres": _split(opts_row["trimestres"])  if opts_row else [],
        "municipios": _split(opts_row["municipios"])  if opts_row else [],
        "statuses":   _split(opts_row["statuses"])    if opts_row else ["NORMAL", "SUSPEITA", "POSITIVO", "FOCO"],
    }

    return {
        "total":          total,
        "page":           page,
        "per_page":       per_page,
        "items":          items,
        "filter_options": filter_options,
    }
