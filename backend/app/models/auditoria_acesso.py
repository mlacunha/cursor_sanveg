from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base


class AuditoriaAcesso(Base):
    __tablename__ = "auditoria_acesso"

    id = Column(String(36), primary_key=True)
    id_usuario = Column(String(36), ForeignKey("users.id"), nullable=False)
    recurso_acessado = Column(String(255), nullable=False)
    tipo_acao = Column(String(50), nullable=False) # Ex: VIEW_PHOTO, VIEW_PDF
    data_hora = Column(DateTime, server_default=func.now())
    ip_origem = Column(String(45), nullable=True)

    # Relacionamentos
    usuario = relationship("User", foreign_keys=[id_usuario])
