from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, index=True)
    login = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    nome = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    cpf = Column(String(14), nullable=True)
    telefone = Column(String(64), nullable=True)
    matricula = Column(String(50), nullable=True)
    carteirafiscal = Column(String(50), nullable=True)
    active = Column(Boolean, nullable=False, default=True)
    role = Column(String(20), nullable=False, default='comum')  # 'comum' | 'admin' | 'superusuario'

    id_orgao = Column(String(36), ForeignKey("orgaos.id"), nullable=True)
    id_unidade = Column(String(36), ForeignKey("unidades.id"), nullable=True)
    id_cargo = Column(String(36), ForeignKey("cargos.id"), nullable=True)
    id_formacao = Column(String(36), ForeignKey("formacoes.id"), nullable=True)

    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)

    criado_em = Column(DateTime, nullable=False, server_default=func.now())
    atualizado_em = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relacionamentos
    orgao_data = relationship("Orgao", foreign_keys=[id_orgao], lazy="select")
    unidade_data = relationship("Unidade", foreign_keys=[id_unidade], lazy="select")
    cargo_data = relationship("Cargo", foreign_keys=[id_cargo], lazy="select")
    formacao_data = relationship("Formacao", foreign_keys=[id_formacao], lazy="select")

    @property
    def is_active(self):
        return self.active is True

    def __repr__(self):
        return f"<User(login={self.login}, email={self.email}, role={self.role})>"
