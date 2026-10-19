from sqlalchemy import Column, Integer, String, DateTime, Text, Date
from app.config.database import Base
from datetime import datetime


class Pessoa(Base):
    __tablename__ = "pessoas"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    cpf = Column(String(14), unique=True, nullable=True)
    rg = Column(String(20), nullable=True)
    telefone = Column(String(20), nullable=True)
    celular = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    endereco = Column(Text, nullable=True)
    cidade = Column(String(100), nullable=True)
    estado = Column(String(2), nullable=True)
    cep = Column(String(10), nullable=True)
    data_nascimento = Column(Date, nullable=True)
    observacoes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Pessoa(id={self.id}, nome={self.nome})>"
