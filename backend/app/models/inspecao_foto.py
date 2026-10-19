from sqlalchemy import Column, String, DECIMAL, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base


from geoalchemy2 import Geometry
from app.models.geo_mixin import GeoMixin

class InspecaoFoto(GeoMixin, Base):
    """
    Foto georreferenciada vinculada a um AreaPrograma (inspeção de praga).
    Armazena o caminho físico do arquivo e as coordenadas GPS extraídas do EXIF.
    """
    __tablename__ = "inspecoes_fotos"

    id = Column(String(36), primary_key=True, nullable=False)

    # FK → area_programa.id  (nome real da tabela no banco)
    id_area_programa = Column(
        String(36),
        # FK declarada no banco pela migration SQL; aqui omitimos ForeignKey()
        # para não depender de ordem de criação pelo SQLAlchemy em ambientes
        # onde a tabela já existe. A constraint é gerenciada pelo banco.
        nullable=False,
        index=True,
    )

    arquivo_nome = Column(String(255), nullable=False)    # nome original (sanitizado)
    arquivo_path = Column(String(500), nullable=False)    # caminho relativo (storage/fotos/…)
    geom         = Column(Geometry('POINT', srid=4326), nullable=True)
    data_captura = Column(DateTime, server_default=func.now(), nullable=True)
    descricao    = Column(String(255), nullable=True)

