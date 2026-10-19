from sqlalchemy import Column, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config.database import Base


class Orgao(Base):
    __tablename__ = "orgaos"
    
    id = Column(String(36), primary_key=True, index=True)
    sigla = Column(String(20), nullable=True)
    nome = Column(String(100), nullable=False)
    id_tipo_orgao = Column(String(36), ForeignKey("orgaos_tipos.id"), nullable=True)
    cnpj = Column(String(20), nullable=True)
    logo = Column(String(255), nullable=True, default="")
    url_logo = Column(String(255), nullable=True, default="")
    servidor_logo = Column(String(255), nullable=True, default="")
    UF_sede = Column(String(10), nullable=True, default="")
    criado_em = Column(TIMESTAMP, nullable=False, server_default=func.now())
    atualizado_em = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
    
    orgao_tipo_data = relationship("OrgaoTipo", foreign_keys=[id_tipo_orgao])
    
    def __repr__(self):
        return f"<Orgao(id={self.id}, sigla={self.sigla}, nome={self.nome})>"
