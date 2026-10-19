from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base


class RegMetas(Base):
    __tablename__ = "reg_metas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    programa = Column(
        String(36),
        ForeignKey("programas.id"),
        nullable=False
    )
    descricao = Column(Integer, nullable=False)
    ano = Column(Integer, nullable=False)
    trimestre = Column(Integer, nullable=False)
    und = Column(String(20), nullable=False)

    programa_data = relationship("Programa", foreign_keys=[programa])
