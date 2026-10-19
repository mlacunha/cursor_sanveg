from sqlalchemy import Column, String, TIMESTAMP, func
from app.config.database import Base


class Produtor(Base):
    __tablename__ = "produtores"

    id = Column(String(36), primary_key=True, index=True)
    n_cadastro = Column(String(50), nullable=True)
    cpf_cnpj = Column(String(20), nullable=True)
    RG_IE = Column(String(20), nullable=True)
    nome = Column(String(100), nullable=False)
    CEP = Column(String(10), nullable=True)
    endereco = Column(String(200), nullable=True)
    bairro = Column(String(100), nullable=True)
    municipio = Column(String(255), nullable=True)
    uf = Column(String(2), nullable=True)
    telefone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
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
