from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base


class Unidade(Base):
    __tablename__ = "unidades"

    id = Column(String(36), primary_key=True, index=True)
    id_orgao = Column(String(36), ForeignKey("orgaos.id"), nullable=True)
    nome = Column(String(255), nullable=False)
    municipio = Column(String(100), nullable=True)
    uf = Column(String(10), nullable=True)

    orgao_data = relationship("Orgao", foreign_keys=[id_orgao])
