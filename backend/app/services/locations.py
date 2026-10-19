"""Utilities to attach Estado and Municipio objects to records returned by APIs.

Provides a small helper `attach_location_info` that inspects a record for
`uf`/`UF`/`estado` and `municipio` fields and, when possible, attaches
`uf_info` (Estado) and `municipio_info` (Municipio) attributes to the object.
"""
from typing import Optional
from sqlalchemy.orm import Session
from app.models.estado import Estado
from app.models.municipio import Municipio


def attach_location_info(record, db: Session) -> None:
    """Attach `uf_info` and `municipio_info` to `record` in-place.

    - Looks for attributes `uf`/`UF`/`estado` (sigla) and `municipio` (name)
    - If `uf` found, loads matching Estado as `uf_info`
    - If `municipio` found and an Estado was identified, tries to load Municipio by name+estado
    """
    # Determine UF sigla
    sigla = None
    for attr in ("uf", "UF", "estado", "estado_sigla"):
        val = getattr(record, attr, None)
        if val:
            sigla = str(val).strip().upper()
            break

    estado_obj = None
    if sigla:
        estado_obj = db.query(Estado).filter(Estado.sigla == sigla).first()
        if estado_obj:
            setattr(record, "uf_info", estado_obj)

    # Determine municipio name
    municipio_name = None
    for attr in ("municipio", "municipio_nome", "municipio_name"):
        val = getattr(record, attr, None)
        if val:
            municipio_name = str(val).strip()
            break

    if municipio_name and estado_obj:
        m = db.query(Municipio).filter(
            Municipio.nome == municipio_name,
            Municipio.estado_id == estado_obj.id,
        ).first()
        if m:
            setattr(record, "municipio_info", m)

    # If we don't have estado but we do have a municipio name, try to find a matching
    # municipio (first match) and attach both municipio_info and derived uf_info.
    if municipio_name and not estado_obj:
        m = db.query(Municipio).filter(Municipio.nome == municipio_name).first()
        if m:
            setattr(record, "municipio_info", m)
            est = db.query(Estado).filter(Estado.id == m.estado_id).first()
            if est:
                setattr(record, "uf_info", est)


def attach_location_info_batch(records, db: Session) -> None:
    """Attach uf_info and municipio_info to a list of records in batch.

    This reduces DB roundtrips by fetching all needed Estados and Municipios
    in a few queries and then mapping them back to the records.
    """
    recs = list(records)
    if not recs:
        return

    # Extract siglas and municipio names from records
    siglas = set()
    municipio_names = set()
    metas = []
    for r in recs:
        sigla = None
        for attr in ("uf", "UF", "estado", "estado_sigla"):
            val = getattr(r, attr, None)
            if val:
                sigla = str(val).strip().upper()
                siglas.add(sigla)
                break

        municipio_name = None
        for attr in ("municipio", "municipio_nome", "municipio_name"):
            val = getattr(r, attr, None)
            if val:
                municipio_name = str(val).strip()
                municipio_names.add(municipio_name)
                break

        metas.append((r, sigla, municipio_name))

    # Bulk fetch estados and municipios
    estados = {}
    if siglas:
        q = db.query(Estado).filter(Estado.sigla.in_(list(siglas))).all()
        estados = {e.sigla: e for e in q}

    municipios = []
    if municipio_names:
        municipios = db.query(Municipio).filter(Municipio.nome.in_(list(municipio_names))).all()

    municipios_by_name = {}
    municipios_by_key = {}
    for m in municipios:
        municipios_by_name.setdefault(m.nome, []).append(m)
        municipios_by_key[(m.estado_id, m.nome)] = m

    # Attach results back to records
    for r, sigla, muni_name in metas:
        estado_obj = None
        if sigla and sigla in estados:
            estado_obj = estados[sigla]
            setattr(r, "uf_info", estado_obj)

        if muni_name:
            # Prefer match by (estado, nome) when possible
            m = None
            if estado_obj and (estado_obj.id, muni_name) in municipios_by_key:
                m = municipios_by_key[(estado_obj.id, muni_name)]
            elif muni_name in municipios_by_name:
                # best-effort: pick first match
                m = municipios_by_name[muni_name][0]
                # if we don't have uf_info yet, set it based on the found municipio
                if not estado_obj:
                    est = db.query(Estado).filter(Estado.id == m.estado_id).first()
                    if est:
                        setattr(r, "uf_info", est)

            if m:
                setattr(r, "municipio_info", m)
