from sqlalchemy import Column, String, Integer, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base

from geoalchemy2 import Geometry
from app.models.geo_mixin import GeoMixin

class RelatorioMapa(GeoMixin, Base):
    __tablename__ = "relatorio_mapa"

    # Agora `id` é INT autoincrement e chave primária única
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Referência ao programa (obrigatório)
    id_programa = Column(String(36), ForeignKey("programas.id"), nullable=False)

    # Campos gerados automaticamente por trigger
    ano = Column(String(4), nullable=True)
    trimestre = Column(Integer, nullable=True)

    # Campos obrigatórios/obrigatórios no schema: `data` e `id_programa`
    data = Column(String(255), nullable=False)

    # Campos que podem ser nulos (facultativos)
    id_orgao = Column(String(36), ForeignKey("orgaos.id"), nullable=True)
    id_usuario = Column(String(36), ForeignKey("users.id"), nullable=True)
    termo_inspecao = Column(Integer, nullable=True)
    termo_coleta = Column(Integer, nullable=True)

    # A relação com `propriedades` é facultativa
    id_propriedade = Column(String(36), ForeignKey("propriedades.id"), nullable=True)
    tipo_imovel = Column(String(60), nullable=True)
    municipio = Column(String(60), nullable=True)
    cultura = Column(String(30), nullable=True)
    status = Column(String(30), nullable=True)

    # Campos opcionais
    # Campos opcionais
    geom = Column(Geometry('POINT', srid=4326), nullable=True)

    # Relacionamentos opcionais
    programa_data = relationship("Programa", foreign_keys=[id_programa])
    orgao_data = relationship("Orgao", foreign_keys=[id_orgao])
    usuario_data = relationship(
        "User",
        foreign_keys=[id_usuario],
        primaryjoin="RelatorioMapa.id_usuario == User.id",
        lazy="select"
    )
    propriedade_data = relationship("Propriedade", foreign_keys=[id_propriedade])

