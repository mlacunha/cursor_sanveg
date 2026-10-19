from sqlalchemy import Column, Integer, String, ForeignKey
from app.config.database import Base
from geoalchemy2 import Geometry

class Municipio(Base):
    __tablename__ = "municipios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    estado_id = Column(Integer, ForeignKey("estados.id"), nullable=False)
    geom = Column(Geometry('MULTIPOLYGON', srid=4326), nullable=True)
