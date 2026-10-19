from sqlalchemy import Column, String, Integer, Float, Date
from app.config.database import Base
from geoalchemy2 import Geometry

class MapaLevantamento(Base):
    """
    Modelo que mapeia a VIEW vw_mapa_levantamentos.
    Esta view unifica dados do 'legado' (relatorio_mapa) e do 'app' (area_inspecionada).
    """
    __tablename__ = "vw_mapa_levantamentos"

    # Mapeamos 'id' como primary_key para satisfazer o SQLAlchemy
    id = Column(String, primary_key=True)
    
    nome_programa = Column(String)
    id_programa = Column(String)
    ano = Column(String)
    trimestre = Column(Integer)
    municipio = Column(String)
    nome_propriedade = Column(String)
    tipo_imovel = Column(String, nullable=True)
    cultura = Column(String)
    
    # Coordenadas como Float (calculadas na View via ST_X/ST_Y)
    latitude = Column(Float)
    longitude = Column(Float)
    
    status = Column(String)
    data = Column(Date)
    uf = Column(String)
    fonte = Column(String)
    municipio_id = Column(Integer, nullable=True)
    
    # Campo geométrico binário do PostGIS
    geom = Column(Geometry('POINT', srid=4326))
