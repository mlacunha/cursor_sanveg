from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Text, DECIMAL
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base


from geoalchemy2 import Geometry
from app.models.geo_mixin import GeoMixin

class AreaInspecionada(GeoMixin, Base):
    """
    Representa o LOCAL FÍSICO inspecionado dentro da propriedade.
    Possui coordenadas geográficas próprias (ponto real da inspeção em campo).
    Os dados de inspeção por praga (programa) ficam em AreaPrograma.
    """
    __tablename__ = "area_inspecionada"

    id = Column(String(36), primary_key=True, nullable=False)
    id_termo_inspecao = Column(
        String(36),
        ForeignKey("termo_inspecao.id"),
        nullable=False,
        index=True,
    )
    tipo_area = Column(String(40), nullable=True)
    nome_local = Column(String(255), nullable=True)
    geom = Column(Geometry('POINT', srid=4326), nullable=True)
    obs = Column(Text, nullable=True)
    data_criacao = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    data_atualizacao = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)

    termo_inspecao_data = relationship("TermoInspecao", foreign_keys=[id_termo_inspecao])
    programas_inspecionados = relationship(
        "AreaPrograma",
        back_populates="area_data",
        cascade="all, delete-orphan",
        lazy="select",
    )

