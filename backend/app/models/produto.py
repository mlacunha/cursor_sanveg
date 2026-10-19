from sqlalchemy import Column, String, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base


class Produto(Base):
    __tablename__ = "produtos"

    id = Column(String(36), primary_key=True, index=True)
    id_propriedade = Column(
        String(36),
        ForeignKey("propriedades.id"),
        nullable=False
    )
    produto = Column(String(100), nullable=False)
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

    propriedade_data = relationship("Propriedade", foreign_keys=[id_propriedade])
