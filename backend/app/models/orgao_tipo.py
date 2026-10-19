from sqlalchemy import Column, String, TIMESTAMP
from sqlalchemy.sql import func
from app.config.database import Base


class OrgaoTipo(Base):
    __tablename__ = "orgaos_tipos"
    
    id = Column(String(36), primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(String(255), nullable=True)
    criado_em = Column(TIMESTAMP, nullable=False, server_default=func.now())
    atualizado_em = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<OrgaoTipo(id={self.id}, nome={self.nome})>"
