from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base


class RegAtividade(Base):
    __tablename__ = "reg_atividade"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(String(255), nullable=False)
    data = Column(DateTime, nullable=False)
    processo_sei = Column(String(50), nullable=False)
    programa = Column(
        String(36),
        ForeignKey("programas.id"),
        nullable=False
    )
    descricao = Column(Text, nullable=False)

    programa_data = relationship("Programa", foreign_keys=[programa])
