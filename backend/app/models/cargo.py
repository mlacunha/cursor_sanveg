from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base


class Cargo(Base):
    __tablename__ = "cargos"

    id = Column(String(36), primary_key=True, index=True)
    id_orgao = Column(String(36), ForeignKey("orgaos.id"), nullable=True)
    sigla = Column(String(50), nullable=True)
    nome = Column(String(255), nullable=False)
    descricao = Column(String(255), nullable=True)

    orgao_data = relationship("Orgao", foreign_keys=[id_orgao])
