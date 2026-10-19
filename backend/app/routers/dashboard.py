from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, text

from app.config.database import get_db
from app.models.propriedade import Propriedade
from app.models.produtor import Produtor
from app.models.termo_inspecao import TermoInspecao
from app.models.amostra_coletada import AmostraColetada
from app.models.area_inspecionada import AreaInspecionada
from app.models.area_programa import AreaPrograma
from app.models.programa import Programa
from app.utils.security import get_current_user
from app.models.users import User

router = APIRouter(
    prefix="/api/dashboard",
    tags=["dashboard"],
)


@router.get("/")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retorna os dados agregados para o Dashboard principal do PWA.

    Estrutura retornada:
    {
        stats: { total_inspecoes, total_municipios, count_normal, count_suspeita, count_foco },
        mapa_pontos: [ { latitude, longitude, status, municipio, programa, data } ],
        recent_produtores: [ { id, primary, secondary } ],
        recent_propriedades: [ { id, primary, secondary } ],
        recent_inspecoes: [ { id, primary, secondary } ],
        recent_amostras: [ { id, primary, secondary } ]
    }

    Os pontos do mapa e estatísticas de status são obtidos da VIEW vw_levantamentos,
    que combina dados legados (relatorio_mapa) e dados do aplicativo (area_programa).
    """

    # ── Stats via VIEW (combina legado + app) ──────────────────────────────────

    total_inspecoes = db.query(func.count(TermoInspecao.id)).scalar() or 0

    stats_sql = text("""
        SELECT
            COUNT(DISTINCT municipio)            AS total_municipios,
            COUNT(*) FILTER (WHERE status = 'NORMAL')               AS count_normal,
            COUNT(*) FILTER (WHERE status = 'SUSPEITA')             AS count_suspeita,
            COUNT(*) FILTER (WHERE status IN ('FOCO', 'POSITIVO'))  AS count_foco
        FROM vw_levantamentos
        WHERE nome_programa IS NOT NULL
    """)
    stats_row = db.execute(stats_sql).mappings().one_or_none()

    total_municipios = int(stats_row["total_municipios"] or 0) if stats_row else 0
    count_normal     = int(stats_row["count_normal"]     or 0) if stats_row else 0
    count_suspeita   = int(stats_row["count_suspeita"]   or 0) if stats_row else 0
    count_foco       = int(stats_row["count_foco"]       or 0) if stats_row else 0

    # ── Pontos do mapa via VIEW (até 500 pontos mais recentes) ─────────────────

    pontos_sql = text("""
        SELECT
            nome_programa,
            nome_propriedade,
            cultura,
            ano,
            trimestre,
            municipio,
            CAST(latitude  AS DECIMAL(10,8)) AS latitude,
            CAST(longitude AS DECIMAL(11,8)) AS longitude,
            status,
            data
        FROM vw_levantamentos
        ORDER BY data DESC
        LIMIT 500
    """)

    pontos_raw = db.execute(pontos_sql).mappings().all()

    mapa_pontos = [
        {
            "nome_programa": p["nome_programa"] or "",
            "programa": p["nome_programa"] or "",
            "nome_propriedade": p["nome_propriedade"] or "",
            "cultura": p["cultura"] or "",
            "ano": str(p["ano"]) if p["ano"] is not None else "",
            "trimestre": str(p["trimestre"]) if p["trimestre"] is not None else "",
            "latitude":  float(p["latitude"])  if p["latitude"]  is not None else None,
            "longitude": float(p["longitude"]) if p["longitude"] is not None else None,
            "status":    p["status"] or "NORMAL",
            "municipio": p["municipio"] or "",
            "data":      str(p["data"]) if p["data"] else "",
        }
        for p in pontos_raw
        if p["latitude"] is not None and p["longitude"] is not None
    ]

    # ── Listas recentes ────────────────────────────────────────────────────────

    recent_produtores = [
        {"id": p.id, "primary": p.nome, "secondary": p.cpf_cnpj or ""}
        for p in db.query(Produtor).order_by(Produtor.criado_em.desc()).limit(5).all()
    ]

    recent_propriedades = [
        {"id": p.id, "primary": p.nome, "secondary": p.municipio or ""}
        for p in db.query(Propriedade).order_by(Propriedade.criado_em.desc()).limit(5).all()
    ]

    # Inspeções recentes com número do termo e nome do(s) programa(s)
    termos_recent = (
        db.query(TermoInspecao)
        .order_by(TermoInspecao.criado_em.desc())
        .limit(5)
        .all()
    )
    recent_inspecoes: list[dict] = []
    for t in termos_recent:
        # Áreas vinculadas ao termo
        area_ids = [
            a.id
            for a in db.query(AreaInspecionada.id)
            .filter(AreaInspecionada.id_termo_inspecao == t.id)
            .all()
        ]
        prog_names: list[str] = []
        if area_ids:
            prog_ids = [
                ap.id_programa
                for ap in db.query(AreaPrograma.id_programa)
                .filter(AreaPrograma.id_area.in_(area_ids))
                .distinct()
                .all()
            ]
            if prog_ids:
                prog_names = [
                    p.nome
                    for p in db.query(Programa)
                    .filter(Programa.id.in_(prog_ids))
                    .all()
                ]
        programa_str = ", ".join(prog_names) if prog_names else ""

        numero = t.numero_ti or f"Ficha {t.ficha_inspecao or t.id[:8]}"
        data_str = str(t.data)[:10] if t.data else ""
        primary = f"{numero} / {data_str}" if data_str else numero

        recent_inspecoes.append(
            {
                "id": t.id,
                "primary": primary,
                "secondary": programa_str,
            }
        )

    # Amostras recentes com número do TCA e programa
    amostras_recent = (
        db.query(AmostraColetada)
        .order_by(AmostraColetada.criado_em.desc())
        .limit(5)
        .all()
    )
    recent_amostras: list[dict] = []
    for a in amostras_recent:
        ap = db.query(AreaPrograma).filter(AreaPrograma.id == a.id_area_programa).first()
        area = (
            db.query(AreaInspecionada).filter(AreaInspecionada.id == ap.id_area).first()
            if ap
            else None
        )
        termo = (
            db.query(TermoInspecao)
            .filter(TermoInspecao.id == area.id_termo_inspecao)
            .first()
            if area
            else None
        )
        prog = (
            db.query(Programa).filter(Programa.id == ap.id_programa).first()
            if ap
            else None
        )

        numero_tc = getattr(termo, "numero_tc", None) if termo else None
        data_tc = str(termo.data)[:10] if termo and termo.data else ""
        primary = (
            f"{numero_tc} / {data_tc}"
            if numero_tc and data_tc
            else (numero_tc or data_tc or "TCA PENDENTE")
        )

        recent_amostras.append(
            {
                "id": a.id,
                "id_termo": termo.id if termo else None,
                "primary": primary,
                "secondary": prog.nome if prog else "",
            }
        )

    return {
        "stats": {
            "total_inspecoes": total_inspecoes,
            "total_municipios": total_municipios,
            "count_normal": count_normal,
            "count_suspeita": count_suspeita,
            "count_foco": count_foco,
        },
        "mapa_pontos": mapa_pontos,
        "recent_produtores": recent_produtores,
        "recent_propriedades": recent_propriedades,
        "recent_inspecoes": recent_inspecoes,
        "recent_amostras": recent_amostras,
    }
