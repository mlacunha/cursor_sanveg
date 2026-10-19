"""Serviço para importar estados (UF) a partir da API do IBGE.

Fornece função `import_estados()` reutilizável por CLI e API.
"""
from typing import Dict, Optional
import requests
from app.config.database import SessionLocal
from app.models.estado import Estado

API_URL = "https://servicodados.ibge.gov.br/api/v1/localidades/estados?orderBy=nome"


def fetch_estados():
    resp = requests.get(API_URL, timeout=10)
    resp.raise_for_status()
    return resp.json()


def import_estados() -> Dict[str, int]:
    """Importa/atualiza todos os estados do IBGE.

    Retorna dict com contagem inserida/atualizada: {'imported': N}
    """
    db = SessionLocal()
    try:
        estados = fetch_estados()
        cnt = 0
        for e in estados:
            regiao = e.get('regiao', {}).get('nome') if e.get('regiao') else None
            existing = db.query(Estado).filter(Estado.id == e['id']).first()
            if existing:
                existing.nome = e['nome']
                existing.sigla = e['sigla']
                existing.regiao = regiao
            else:
                new = Estado(id=e['id'], nome=e['nome'], sigla=e['sigla'], regiao=regiao)
                db.add(new)
            cnt += 1
        db.commit()
        return {'imported': cnt}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
