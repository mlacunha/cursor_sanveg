from sqlalchemy import Column, Integer, String
from app.config.database import Base


class Estado(Base):
    __tablename__ = "estados"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), nullable=False)
    sigla = Column(String(2), nullable=False)
    regiao = Column(String(20), nullable=True)
