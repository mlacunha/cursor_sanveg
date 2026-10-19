from sqlalchemy import Column, String
from app.config.database import Base


class Laboratorio(Base):
    __tablename__ = "laboratorios"

    id = Column(String(64), primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    tipo = Column(String(20), nullable=True)
    cnpj = Column(String(20), nullable=True)
    endereco = Column(String(255), nullable=True)
    cep = Column(String(20), nullable=True)
    cidade = Column(String(120), nullable=True)
    uf = Column(String(2), nullable=True)
    contato = Column(String(255), nullable=True)
    instrumento_reconhecimento = Column(String(255), nullable=True)
    contato_nome = Column(String(255), nullable=True)
    contato_cargo = Column(String(120), nullable=True)
    contato_email = Column(String(255), nullable=True)
    contato_telefone = Column(String(30), nullable=True)
