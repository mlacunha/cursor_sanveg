from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from app.config.database import Base


class Formacao(Base):
    __tablename__ = "formacoes"

    id = Column(String(36), primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    criado_em = Column(DateTime, nullable=False, server_default=func.now())
    atualizado_em = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Formacao(id={self.id}, nome={self.nome})>"
