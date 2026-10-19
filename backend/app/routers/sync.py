"""
Router de sincronização offline/online do PWA.

POST /api/sync/push — recebe fila de operações do IndexedDB e aplica no banco
GET  /api/sync/pull — retorna snapshot completo dos dados para o dispositivo
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, Optional
from pydantic import BaseModel

from app.config.database import get_db
from app.models.users import User
from app.models.programa import Programa
from app.models.hospedeiro import Hospedeiro
from app.models.norma import Norma
from app.models.produtor import Produtor
from app.models.propriedade import Propriedade
from app.models.termo_inspecao import TermoInspecao
from app.models.area_inspecionada import AreaInspecionada
from app.models.area_programa import AreaPrograma
from app.models.amostra_coletada import AmostraColetada
from app.models.orgao_tipo import OrgaoTipo
from app.models.orgao import Orgao
from app.models.unidade import Unidade
from app.models.cargo import Cargo
from app.models.formacao import Formacao
from app.models.controle_sequencial import ControleSequencial
from app.models.laboratorio import Laboratorio
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/sync", tags=["Sincronização"])

# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class SyncQueueItem(BaseModel):
    id: int
    action: str          # 'put' | 'delete'
    route: str           # 'termo_inspecao' | 'area_inspecionada' | ...
    payload: dict[str, Any]
    timestamp: int


class SyncPushRequest(BaseModel):
    queue: list[SyncQueueItem]


class SyncPushResponse(BaseModel):
    processed_ids: list[int]
    errors: list[dict[str, Any]]


# Mapeamento rota → modelo SQLAlchemy
ROUTE_MODEL_MAP = {
    "programas":         Programa,
    "hospedeiros":       Hospedeiro,
    "normas":            Norma,
    "produtores":        Produtor,
    "propriedades":      Propriedade,
    "termo_inspecao":    TermoInspecao,
    "area_inspecionada": AreaInspecionada,
    "area_programa":     AreaPrograma,
    "amostra_coletada":  AmostraColetada,
    "orgaos":            Orgao,
    "unidades":          Unidade,
    "cargos":            Cargo,
    "tipos_orgao":       OrgaoTipo,
    "formacoes":         Formacao,
    "laboratorios":      Laboratorio,
    "usuarios":          User,
}

# Chaves primárias simples para todas as rotas (sem compostas)
COMPOSITE_PKS: dict = {}


def _get_model_columns(model) -> set[str]:
    """Retorna o conjunto de colunas válidas do modelo."""
    return {c.key for c in model.__table__.columns}


def _get_fk_columns(model) -> set[str]:
    """Retorna nomes das colunas que são chaves estrangeiras."""
    return {c.key for c in model.__table__.columns if c.foreign_keys}


def _get_numeric_columns(model) -> set[str]:
    """Retorna nomes das colunas numéricas (Integer, Numeric/Decimal, Float)."""
    from sqlalchemy import Integer, Numeric, Float
    return {
        c.key for c in model.__table__.columns
        if isinstance(c.type, (Integer, Numeric, Float))
    }


def _get_datetime_columns(model) -> set[str]:
    """Retorna nomes das colunas de data/hora (Date, DateTime, TIMESTAMP)."""
    from sqlalchemy import Date, DateTime, TIMESTAMP

    datetime_types = (Date, DateTime, TIMESTAMP)
    return {
        c.key for c in model.__table__.columns
        if isinstance(c.type, datetime_types)
    }


VALID_RESULTADOS_LAB = {
    "NEGATIVO",
    "POSITIVO",
    "INCONCLUSIVO",
    "AMOSTRA_REJEITADA",
    "AMOSTRA_INVALIDA",
}


def _normalize_resultado_laboratorio(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None

    normalized = value.strip().upper()
    if not normalized:
        return None

    normalized = {
        "AMOSTRA REJEITADA": "AMOSTRA_REJEITADA",
        "AMOSTRA INVALIDA": "AMOSTRA_INVALIDA",
    }.get(normalized, normalized)

    if normalized not in VALID_RESULTADOS_LAB:
        raise ValueError("resultado_laboratorio invalido")

    return normalized


def _authorize_user_sync(db: Session, payload: dict, current_user: User) -> None:
    """Aplica regras de permissao para alteracoes sincronizadas de usuarios."""
    existing = db.get(User, payload.get("id")) if payload.get("id") else None

    if current_user.role == "superusuario":
        return

    if current_user.role == "admin":
        target_orgao = payload.get("id_orgao")
        if existing:
            if existing.role == "superusuario":
                raise PermissionError("admin nao pode alterar superusuario via sync")
            if existing.id_orgao != current_user.id_orgao:
                raise PermissionError("admin so pode alterar usuarios do proprio orgao")
            if target_orgao is not None and target_orgao != current_user.id_orgao:
                raise PermissionError("admin nao pode mover usuario para outro orgao")
        else:
            if payload.get("role") == "superusuario":
                raise PermissionError("admin nao pode criar superusuario via sync")
            if target_orgao != current_user.id_orgao:
                raise PermissionError("admin so pode criar usuarios do proprio orgao")
        return

    if not existing or existing.id != current_user.id:
        raise PermissionError("usuario comum so pode sincronizar o proprio cadastro")

    forbidden_fields = {"role", "active", "id_orgao", "id_unidade", "id_cargo", "id_formacao", "login"}
    if forbidden_fields.intersection(payload.keys()):
        raise PermissionError("usuario comum nao pode alterar privilegios ou vinculacoes via sync")


def _apply_put(db: Session, route: str, payload: dict, current_user: User) -> None:
    """INSERT OR UPDATE via merge do SQLAlchemy."""
    Model = ROUTE_MODEL_MAP.get(route)
    if Model is None:
        raise ValueError(f"Rota desconhecida: '{route}'")

    valid_cols = _get_model_columns(Model)
    fk_cols = _get_fk_columns(Model)
    numeric_cols = _get_numeric_columns(Model)
    datetime_cols = _get_datetime_columns(Model)
    # Mantém o payload bruto para regras específicas por rota
    raw_payload = dict(payload)
    clean = {k: v for k, v in raw_payload.items() if k in valid_cols}

    # Converte string vazia → None em colunas FK e numéricas
    for col in fk_cols | numeric_cols:
        if col in clean and clean[col] == "":
            clean[col] = None

    # Normaliza datas/datetimes em formato ISO (ex: '2026-03-13T01:28:04.753Z')
    for col in datetime_cols:
        val = clean.get(col)
        if isinstance(val, str):
            s = val.strip()
            if not s:
                continue
            # Remove o sufixo 'Z' (UTC) se presente
            if s.endswith("Z"):
                s = s[:-1]
            # Se vier com milissegundos, corta em segundos
            # Ex: '2026-03-13T01:28:04.753' -> '2026-03-13T01:28:04'
            if "T" in s and "." in s:
                before_dot, _, _rest = s.partition(".")
                s = before_dot
            # Converte 'T' para espaço: 'YYYY-MM-DDTHH:MM:SS' -> 'YYYY-MM-DD HH:MM:SS'
            if "T" in s:
                s = s.replace("T", " ")
            clean[col] = s

    # Tratamento especial para usuários
    if route == "usuarios":
        from app.utils.security import get_password_hash
        existing = db.get(User, clean.get("id")) if clean.get("id") else None

        if existing and "login" not in raw_payload:
            clean["login"] = existing.login
        # Se login não veio, usa o email como login
        if not clean.get("login") and clean.get("email"):
            clean["login"] = clean["email"]

        if existing and not clean.get("login"):
            clean["login"] = existing.login

        existing_by_login = (
            db.query(User).filter(User.login == clean.get("login")).first()
            if clean.get("login")
            else None
        )
        if existing_by_login and existing_by_login.id != clean.get("id"):
            raise ValueError("login ja cadastrado")

        existing_by_email = (
            db.query(User).filter(User.email == clean.get("email")).first()
            if clean.get("email")
            else None
        )
        if existing_by_email and existing_by_email.id != clean.get("id"):
            raise ValueError("email ja cadastrado")

        # Trata a senha
        pwd = clean.get("password")
        if pwd and not str(pwd).startswith("$2b$"):
            # Texto plano: faz o hash antes de salvar
            clean["password"] = get_password_hash(pwd)
        elif not pwd:
            # Sem senha no payload: mantém a senha existente no banco
            if existing and existing.password:
                clean["password"] = existing.password
            else:
                # Novo usuário sem senha: define senha temporária
                clean["password"] = get_password_hash("Mudar@1234")

    # Tratamento especial para termo_inspecao (numeração do termo de inspeção)
    if route == "termo_inspecao":
        from datetime import datetime

        manual_flag = bool(raw_payload.get("termo_manual"))
        provided_num = (raw_payload.get("termo_inspecao") or "").strip()

        termo_id = clean.get("id")
        existing = db.get(TermoInspecao, termo_id) if termo_id else None

        if manual_flag:
            # Numeração manual: usa exatamente o valor digitado, sem mexer no sequencial
            if provided_num:
                clean["numero_ti"] = provided_num
            elif existing and getattr(existing, "numero_ti", None):
                clean["numero_ti"] = existing.numero_ti
        else:
            # Numeração automática
            # Se o termo já possui número gravado no banco, não renumerar
            if existing and getattr(existing, "numero_ti", None):
                pass
            else:
                # Determina o ano a partir da data da inspeção
                dt_val = clean.get("data") or (existing.data if existing else None)
                ano_str: str
                if isinstance(dt_val, str) and len(dt_val) >= 4:
                    ano_str = dt_val[:4]
                elif hasattr(dt_val, "year"):
                    ano_str = str(dt_val.year)
                else:
                    ano_str = datetime.utcnow().strftime("%Y")

                # Busca o usuário para obter carteira fiscal / matrícula / login
                user_id = clean.get("id_usuario") or (existing.id_usuario if existing else None)
                user = db.get(User, user_id) if user_id else None

                if user:
                    ident = user.carteirafiscal or user.matricula or user.login

                    # Controle sequencial por login + ano
                    controle = (
                        db.query(ControleSequencial)
                        .filter(
                            ControleSequencial.login == user.login,
                            ControleSequencial.ano == ano_str,
                        )
                        .first()
                    )

                    if not controle:
                        controle = ControleSequencial(
                            login=user.login,
                            ano=ano_str,
                            seq_ti=0,
                            seq_tc=0,
                        )
                        db.add(controle)
                        db.flush()

                    controle.seq_ti = (controle.seq_ti or 0) + 1
                    seq = controle.seq_ti

                    # ficha_inspecao mantém o sequencial numérico interno
                    clean.setdefault("ficha_inspecao", seq)
                    # numero_ti é o número exibido no termo: SEQ/IDENT/ANO
                    clean["numero_ti"] = f"{seq}/{ident}/{ano_str}"

    # Tratamento especial para area_programa (normalização de resultado)
    if route == "area_programa":
        raw_res = (raw_payload.get("resultado") or "").upper().strip()
        if raw_res:
            if "SUSPEITA" in raw_res:
                clean["resultado"] = "SUSPEITA"
            elif "FOCO" in raw_res or "POSITIVO" in raw_res:
                clean["resultado"] = "POSITIVO"
            else:
                clean["resultado"] = "NORMAL"

    # Tratamento especial para amostra_coletada (numeração do termo de coleta)
    if route == "amostra_coletada":
        from datetime import datetime
        from app.models.area_inspecionada import AreaInspecionada

        manual_flag = bool(raw_payload.get("termo_coleta_manual"))
        provided_tc = (raw_payload.get("termo_coleta") or "").strip()
        normalized_lab_result = _normalize_resultado_laboratorio(
            raw_payload.get("resultado_laboratorio")
        )
        if "resultado_laboratorio" in raw_payload:
            clean["resultado_laboratorio"] = normalized_lab_result

        ap_id = clean.get("id_area_programa")
        termo = None
        user = None
        area_programa = None
        existing_amostra = db.get(AmostraColetada, clean.get("id")) if clean.get("id") else None

        if ap_id:
            area_programa = db.get(AreaPrograma, ap_id)
            if area_programa:
                ai = db.get(AreaInspecionada, area_programa.id_area)
                if ai:
                    termo = db.get(TermoInspecao, ai.id_termo_inspecao)
                    if termo:
                        user = db.get(User, termo.id_usuario) if termo.id_usuario else None
            else:
                raise ValueError("area_programa vinculada a amostra nao encontrada")

        if termo and user:
            if manual_flag:
                # Numeração manual do Termo de Coleta: grava valor digitado
                if provided_tc:
                    termo.numero_tc = provided_tc
            else:
                # Numeração automática apenas se ainda não existir número de coleta
                if not getattr(termo, "numero_tc", None):
                    dt_val = termo.data
                    if isinstance(dt_val, str) and len(dt_val) >= 4:
                        ano_str = dt_val[:4]
                    elif hasattr(dt_val, "year"):
                        ano_str = str(dt_val.year)
                    else:
                        ano_str = datetime.utcnow().strftime("%Y")

                    ident = user.carteirafiscal or user.matricula or user.login

                    controle = (
                        db.query(ControleSequencial)
                        .filter(
                            ControleSequencial.login == user.login,
                            ControleSequencial.ano == ano_str,
                        )
                        .first()
                    )
                    if not controle:
                        controle = ControleSequencial(
                            login=user.login,
                            ano=ano_str,
                            seq_ti=0,
                            seq_tc=0,
                        )
                        db.add(controle)
                        db.flush()

                    controle.seq_tc = (controle.seq_tc or 0) + 1
                    seq_tc = controle.seq_tc

                    # termo_coleta: sequencial numérico interno
                    if termo.termo_coleta is None:
                        termo.termo_coleta = seq_tc
                    # numero_tc: número exibido no TCA
                    termo.numero_tc = f"{seq_tc}/{ident}/{ano_str}"

        previous_resultado = (
            _normalize_resultado_laboratorio(getattr(existing_amostra, "resultado_laboratorio", None))
            if existing_amostra
            else None
        )
        if (
            area_programa
            and clean.get("data_resultado")
            and normalized_lab_result
            and normalized_lab_result != previous_resultado
        ):
            if normalized_lab_result == "POSITIVO":
                if area_programa.resultado != "POSITIVO":
                    area_programa.resultado = "POSITIVO"
            elif normalized_lab_result == "NEGATIVO":
                if area_programa.resultado != "NORMAL":
                    area_programa.resultado = "NORMAL"

    existing_record = db.get(Model, clean.get("id")) if clean.get("id") else None

    # O-BAC and Immutability Checks
    if existing_record and hasattr(existing_record, 'status_homologacao'):
        if current_user.role != 'superusuario':
            # 1. Immutability
            if getattr(existing_record, 'status_homologacao') == 'homologado':
                raise PermissionError(f"Registro homologado nao pode ser alterado via sync na rota {route}")
            
            # 2. O-BAC
            record_usuario = getattr(existing_record, 'id_usuario', None)
            record_orgao = getattr(existing_record, 'id_orgao', None)

            if current_user.role == 'fiscal':
                if record_usuario and record_usuario != current_user.id:
                    raise PermissionError(f"Acesso negado: Registro pertence a outro autor. {route}")
            elif current_user.role in ['admin', 'admin_estadual']:
                if record_orgao and record_orgao != current_user.id_orgao:
                    raise PermissionError(f"Acesso negado: Registro pertence a outro orgao. {route}")

    # Inject Authorship logic for new entries
    if not existing_record:
        if 'id_usuario' in valid_cols and clean.get('id_usuario') is None:
            clean['id_usuario'] = current_user.id
        if 'id_orgao' in valid_cols and clean.get('id_orgao') is None:
            clean['id_orgao'] = current_user.id_orgao
        if 'status_homologacao' in valid_cols and clean.get('status_homologacao') is None:
            clean['status_homologacao'] = 'aberto'

    instance = Model(**clean)
    db.merge(instance)


def _apply_delete(db: Session, route: str, payload: dict, current_user: User) -> None:
    """DELETE pelo ID (simples ou composto)."""
    Model = ROUTE_MODEL_MAP.get(route)
    if Model is None:
        raise ValueError(f"Rota desconhecida: '{route}'")

    pk_fields = COMPOSITE_PKS.get(route, ("id",))
    pk_values = {f: payload.get(f) for f in pk_fields}

    if any(v is None for v in pk_values.values()):
        raise ValueError(f"Payload sem chave primária para rota '{route}': {pk_values}")

    instance = db.get(Model, tuple(pk_values.values()) if len(pk_values) > 1 else list(pk_values.values())[0])
    if instance:
        # OBAC and Immutability checks
        if hasattr(instance, 'status_homologacao'):
            if current_user.role != 'superusuario':
                # 1. Immutability
                if getattr(instance, 'status_homologacao') == 'homologado':
                    raise PermissionError(f"Registro homologado nao pode ser excluido na rota {route}")
                
                # 2. O-BAC
                record_usuario = getattr(instance, 'id_usuario', None)
                record_orgao = getattr(instance, 'id_orgao', None)

                if current_user.role == 'fiscal':
                    if record_usuario and record_usuario != current_user.id:
                        raise PermissionError(f"Acesso negado: Registro pertence a outro autor. {route}")
                elif current_user.role in ['admin', 'admin_estadual']:
                    if record_orgao and record_orgao != current_user.id_orgao:
                        raise PermissionError(f"Acesso negado: Registro pertence a outro orgao. {route}")

        db.delete(instance)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/push", response_model=SyncPushResponse)
def sync_push(
    body: SyncPushRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Recebe a fila de operações offline do PWA e aplica no banco de dados.
    Retorna IDs processados e erros por item.
    """
    processed_ids = []
    errors = []

    for item in body.queue:
        try:
            with db.begin_nested():
                if item.route == "usuarios":
                    _authorize_user_sync(db, item.payload, current_user)

                if item.action == "put":
                    _apply_put(db, item.route, item.payload, current_user)
                elif item.action == "delete":
                    _apply_delete(db, item.route, item.payload, current_user)
                else:
                    raise ValueError(f"Ação desconhecida: '{item.action}'")

                db.flush()
            processed_ids.append(item.id)

        except Exception as exc:
            errors.append({"id": item.id, "route": item.route, "error": str(exc)})

    if processed_ids:
        db.commit()

    return SyncPushResponse(processed_ids=processed_ids, errors=errors)


@router.get("/pull")
def sync_pull(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retorna snapshot completo dos dados do banco para o PWA.
    O frontend fará bulkPut em cada tabela do IndexedDB.
    """

    def serialize(obj) -> dict:
        """Converte uma instância ORM num dict simples (sem relacionamentos lazy)."""
        from geoalchemy2.types import Geometry
        return {
            c.key: getattr(obj, c.key)
            for c in obj.__table__.columns
            if not isinstance(c.type, Geometry) and c.key != "geom"
        }

    def fmt_date(v):
        return v.isoformat() if v else None

    def rows(Model) -> list[dict]:
        items = db.query(Model).all()
        result = []
        for obj in items:
            d = serialize(obj)
            # Campos especiais para termo_inspecao (compatibilidade com o PWA)
            if Model is TermoInspecao:
                data_val = getattr(obj, "data", None)
                if data_val is not None:
                    try:
                        d["data_inspecao"] = data_val.date().isoformat()
                    except AttributeError:
                        d["data_inspecao"] = str(data_val)[:10]
                else:
                    d["data_inspecao"] = None

                numero_ti = getattr(obj, "numero_ti", None)
                ficha = getattr(obj, "ficha_inspecao", None)
                d["termo_inspecao"] = numero_ti or (str(ficha) if ficha is not None else "")
                # No retorno padrão consideramos que o número veio do sistema (não manual)
                d["termo_manual"] = False

                # Termo de Coleta (TCA)
                numero_tc = getattr(obj, "numero_tc", None)
                termo_coleta = getattr(obj, "termo_coleta", None)
                d["termo_coleta"] = numero_tc or (str(termo_coleta) if termo_coleta is not None else "")
                d["termo_coleta_manual"] = False
            # Converter datetime → string ISO para JSON
            for k, val in d.items():
                if hasattr(val, "isoformat"):
                    d[k] = val.isoformat()
            result.append(d)
        return result

    return {
        "programas":         rows(Programa),
        "hospedeiros":       rows(Hospedeiro),
        "normas":            rows(Norma),
        "produtores":        rows(Produtor),
        "propriedades":      rows(Propriedade),
        "termo_inspecao":    rows(TermoInspecao),
        "area_inspecionada": rows(AreaInspecionada),
        "area_programa":     rows(AreaPrograma),
        "amostra_coletada":  rows(AmostraColetada),
        "tipos_orgao":       rows(OrgaoTipo),
        "orgaos":            rows(Orgao),
        "unidades":          rows(Unidade),
        "cargos":            rows(Cargo),
        "formacoes":         rows(Formacao),
        "laboratorios":      rows(Laboratorio),
        "usuarios":          [
            {k: v for k, v in serialize(u).items()
             if k not in ("password", "reset_token", "reset_token_expires")}
            for u in db.query(User).filter(User.active == True).all()
        ],
    }
