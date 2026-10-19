from sqlalchemy import Column, String, Text, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship
from app.config.database import Base


class Norma(Base):
    __tablename__ = "normas"

    id = Column(String(36), primary_key=True, index=True)
    id_programa = Column(String(36), ForeignKey("programas.id"), nullable=False)
    nome_norma = Column(String(255), nullable=False)
    ementa = Column(Text, nullable=False)
    url_publicacao = Column(String(512), nullable=True)
    criado_em = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now()
    )
    atualizado_em = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationship to Programa
    programa = relationship("Programa", foreign_keys=[id_programa])
