from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship
from app.config.database import Base


class Hospedeiro(Base):
    __tablename__ = "hospedeiros"

    id = Column(String(36), primary_key=True, index=True)
    id_programa = Column(String(36), ForeignKey("programas.id"), nullable=False)
    nomes_comuns = Column(String(255), nullable=False)
    nome_cientifico = Column(String(255), nullable=False)
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
