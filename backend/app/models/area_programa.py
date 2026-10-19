from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, DECIMAL, Text, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base


from geoalchemy2 import Geometry
from app.models.geo_mixin import GeoMixin

class AreaPrograma(GeoMixin, Base):
    """
    Representa a INSPEÇÃO DE UMA PRAGA (programa) em uma área física específica.
    Uma área pode ter múltiplos registros, um por programa inspecionado.
    """
    __tablename__ = "area_programa"

    id = Column(String(36), primary_key=True, nullable=False)
    id_area = Column(String(36), ForeignKey("area_inspecionada.id"), nullable=False, index=True)
    id_programa = Column(String(36), ForeignKey("programas.id"), nullable=False, index=True)

    especie = Column(String(40), nullable=True)
    variedade = Column(String(255), nullable=True)
    material_multiplicacao = Column(String(120), nullable=True)
    origem = Column(String(120), nullable=True)
    idade_plantio = Column(DECIMAL(10, 2), nullable=True)
    area_plantada = Column(DECIMAL(10, 2), nullable=True)
    numero_plantas = Column(Integer, nullable=True)
    numero_inspecionadas = Column(Integer, nullable=True)
    numero_suspeitas = Column(Integer, nullable=True)
    # Coordenadas específicas da inspeção daquele programa na área
    geom = Column(Geometry('POINT', srid=4326), nullable=True)
    # Resultado consolidado para o programa na área: NORMAL | SUSPEITA | POSITIVO
    resultado = Column(String(60), nullable=True)
    obs = Column(Text, nullable=True)

    data_criacao = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    data_atualizacao = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)

    area_data = relationship("AreaInspecionada", back_populates="programas_inspecionados")
    programa_data = relationship("Programa", foreign_keys=[id_programa])
    amostras = relationship(
        "AmostraColetada",
        back_populates="area_programa_data",
        cascade="all, delete-orphan",
        lazy="select",
    )

