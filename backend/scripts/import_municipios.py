"""
Script para importar/atualizar a tabela `municipios` a partir da API do IBGE.
Uso: python scripts/import_municipios.py [--estado SIGLA]
Se `--estado` não for fornecido, importa municípios para todos os estados registrados.
"""
import argparse
import requests
from app.config.database import SessionLocal
from app.models.estado import Estado
from app.models.municipio import Municipio

IBGE_URL_TEMPLATE = "https://servicodados.ibge.gov.br/api/v1/localidades/estados/{sigla}/municipios"


def fetch_municipios_of_estado(sigla: str):
    url = IBGE_URL_TEMPLATE.format(sigla=sigla)
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()


def import_for_estado(db, estado: Estado):
    municipios = fetch_municipios_of_estado(estado.sigla)
    count = 0
    for m in municipios:
        existing = db.query(Municipio).filter(Municipio.id == m["id"]).first()
        if existing:
            existing.nome = m["nome"]
            existing.estado_id = estado.id
        else:
            new = Municipio(id=m["id"], nome=m["nome"], estado_id=estado.id)
            db.add(new)
        count += 1
    return count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--estado", help="Sigla do estado (ex: PA). Se omitido, importa todos")
    args = parser.parse_args()

    # Reuse service to perform the import so CLI and API share the same logic
    from app.services.municipios_import import import_municipios

    results = import_municipios(args.estado)
    for sigla, cnt in results.items():
        if sigla == "total":
            continue
        print(f"Imported/updated {cnt} municipios for estado {sigla}")

    print(f"Total municipios imported/updated: {results.get('total', 0)}")


if __name__ == "__main__":
    main()
