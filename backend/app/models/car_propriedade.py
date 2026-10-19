from sqlalchemy import Column, String, Integer, Float, Index
from app.config.database import Base
from geoalchemy2 import Geometry

class CarPropriedade(Base):
    """
    Modelo para armazenar os perímetros e dados básicos do CAR (Cadastro Ambiental Rural).
    """
    __tablename__ = "car_propriedades"

    id = Column(Integer, primary_key=True, index=True)
    
    # Código oficial do CAR (Ex: PA-1501402-...)
    codigo_imovel = Column(String(100), unique=True, index=True, nullable=False)
    
    tipo_imovel = Column(String(50), nullable=True)
    situacao = Column(String(50), nullable=True)
    municipio = Column(String(255), nullable=True)
    sigla_uf = Column(String(2), index=True, nullable=True)
    area_ha = Column(Float, nullable=True)
    
    # Geometria do imóvel (MultiPolygon no SRID 4326)
    geom = Column(Geometry('MULTIPOLYGON', srid=4326), nullable=False)
