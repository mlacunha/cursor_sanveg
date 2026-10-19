from sqlalchemy import Column, String, Integer
from app.config.database import Base


class DashboardFiltros(Base):
    __tablename__ = "dashboard_filtros"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ano = Column(Integer, nullable=True)
    trimestre = Column(Integer, nullable=True)
    id_programa = Column(String(36), nullable=True)
    municipio = Column(String(150), nullable=True)
