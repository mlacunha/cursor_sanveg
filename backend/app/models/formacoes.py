from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from app.config.database import Base
from uuid import uuid4


def _gen_uuid() -> str:
    return str(uuid4())


class Formacao(Base):
    """Formações acadêmicas/profissionais dos usuários."""
    __tablename__ = "formacoes"

    id = Column(String(36), primary_key=True, default=_gen_uuid, index=True)
    nome = Column(String(255), nullable=False)
    criado_em = Column(DateTime, server_default=func.now(), nullable=False)
    atualizado_em = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    def __repr__(self):
        return f"<Formacao(id={self.id}, nome={self.nome})>"
