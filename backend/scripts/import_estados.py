"""
Script para importar/atualizar a tabela `estados` a partir da API do IBGE.
Uso: python scripts/import_estados.py
"""
import json
import requests
from app.config.database import SessionLocal
from app.models.estado import Estado

API_URL = "https://servicodados.ibge.gov.br/api/v1/localidades/estados?orderBy=nome"


def fetch_ibge():
    resp = requests.get(API_URL, timeout=10)
    resp.raise_for_status()
    return resp.json()


def main():
    db = SessionLocal()
    try:
        estados = fetch_ibge()
        for e in estados:
            regiao = None
            if e.get("regiao"):
                regiao = e["regiao"].get("nome")

            existing = db.query(Estado).filter(Estado.id == e["id"]).first()
            if existing:
                existing.nome = e["nome"]
                existing.sigla = e["sigla"]
                existing.regiao = regiao
            else:
                new = Estado(id=e["id"], nome=e["nome"], sigla=e["sigla"], regiao=regiao)
                db.add(new)

        db.commit()
        print(f"Imported/updated {len(estados)} estados")
    except Exception as ex:
        db.rollback()
        print("Erro ao importar estados:", ex)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
