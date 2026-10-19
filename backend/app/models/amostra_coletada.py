from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, DECIMAL, Date, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base


from geoalchemy2 import Geometry
from app.models.geo_mixin import GeoMixin

class AmostraColetada(GeoMixin, Base):
    """
    Representa uma AMOSTRA COLETADA vinculada a uma inspeção de programa em área específica.
    """
    __tablename__ = "amostra_coletada"

    id = Column(String(36), primary_key=True, nullable=False)
    id_area_programa = Column(
        String(36),
        ForeignKey("area_programa.id"),
        nullable=False,
        index=True,
    )

    envelope = Column(String(30), nullable=True)
    parte_coletada = Column(String(255), nullable=True)
    geom = Column(Geometry('POINT', srid=4326), nullable=True)
    data_envio_laboratorio = Column(Date, nullable=True)
    id_laboratorio = Column(String(64), ForeignKey("laboratorios.id"), nullable=True)
    processo_sei = Column(String(100), nullable=True)
    data_resultado = Column(Date, nullable=True)
    resultado_laboratorio = Column(Text, nullable=True)
    laudo_arquivo = Column(String(255), nullable=True)

    criado_em = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    atualizado_em = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)

    area_programa_data = relationship(
        "AreaPrograma",
        back_populates="amostras",
        foreign_keys=[id_area_programa],
        lazy="select",
    )
    laboratorio_data = relationship(
        "Laboratorio",
        foreign_keys=[id_laboratorio],
        lazy="select",
    )
