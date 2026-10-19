from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base


class ControleSequencial(Base):
    __tablename__ = "controle_sequencial"

    login = Column(String(255), ForeignKey("users.login"), primary_key=True)
    ano = Column(String(4), primary_key=True)
    seq_ti = Column(Integer, nullable=False, default=0)
    seq_tc = Column(Integer, nullable=False, default=0)

    usuario_data = relationship(
        "User",
        foreign_keys=[login],
        primaryjoin="ControleSequencial.login == User.login",
        lazy="select"
    )
