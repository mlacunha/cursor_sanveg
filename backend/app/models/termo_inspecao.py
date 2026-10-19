from sqlalchemy import Column, String, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base


class TermoInspecao(Base):
    __tablename__ = "termo_inspecao"

    id = Column(String(36), primary_key=True, index=True)
    data = Column(TIMESTAMP, nullable=False)
    # Número sequencial simples (controle interno, legado)
    ficha_inspecao = Column(Integer, nullable=True)
    # Número completo exibido no sistema (Termo de Inspeção): SEQ/IDENT/ANO (ex: 15/12345/2026)
    numero_ti = Column(String(50), nullable=True)
    # Número sequencial simples do Termo de Coleta (controle interno)
    termo_coleta = Column(Integer, nullable=True)
    # Número completo exibido no sistema (Termo de Coleta): SEQ/IDENT/ANO
    numero_tc = Column(String(50), nullable=True)
    id_usuario = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=True
    )
    id_propriedade = Column(
        String(36),
        ForeignKey("propriedades.id"),
        nullable=False
    )
    criado_em = Column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False
    )
    atualizado_em = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relacionamentos opcionais
    usuario_data = relationship(
        "User",
        foreign_keys=[id_usuario],
        primaryjoin="TermoInspecao.id_usuario == User.id",
        lazy="select"
    )
    propriedade_data = relationship(
        "Propriedade",
        foreign_keys=[id_propriedade],
        lazy="select"
    )
