from sqlalchemy import (
    Column, String, TIMESTAMP, ForeignKey, Double, DECIMAL
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base


from geoalchemy2 import Geometry
from app.models.geo_mixin import GeoMixin

class Propriedade(GeoMixin, Base):
    __tablename__ = "propriedades"

    id = Column(String(36), primary_key=True, index=True)
    n_cadastro = Column(String(50), nullable=True)
    cpf_cnpj = Column(String(20), nullable=True)
    RG_IE = Column(String(20), nullable=True)
    nome = Column(String(100), nullable=False)
    CEP = Column(String(10), nullable=True)
    endereco = Column(String(200), nullable=True)
    bairro = Column(String(100), nullable=True)
    municipio = Column(String(255), nullable=True)
    UF = Column(String(2), nullable=True)
    area_total = Column(Double, nullable=True)
    destino_producao = Column(String(255), nullable=True)
    id_proprietario = Column(
        String(36),
        ForeignKey("produtores.id"),
        nullable=True
    )
    classificacao = Column(String(50), nullable=True)
    producao_familiar = Column(String(3), nullable=True)
    geom = Column(Geometry('POINT', srid=4326), nullable=True)
    criado_em = Column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False
    )
    atualizado_em = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relacionamento opcional com produtor
    proprietario_data = relationship(
        "Produtor",
        foreign_keys=[id_proprietario],
        lazy="select"
    )

