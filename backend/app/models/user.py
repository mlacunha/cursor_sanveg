from sqlalchemy import Column, String, DateTime, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base
from datetime import datetime


class SecUser(Base):
    __tablename__ = "sec_users"
    
    login = Column(String(255), primary_key=True, index=True)
    pswd = Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True, index=True)
    active = Column(String(1), nullable=True, default='Y')
    activation_code = Column(String(32), nullable=True)
    priv_admin = Column(String(1), nullable=True)
    mfa = Column(String(255), nullable=True)
    picture = Column(LargeBinary, nullable=True)
    orgao = Column(String(36), ForeignKey("orgaos.id"), nullable=True)
    unidade = Column(String(36), ForeignKey("unidades.id"), nullable=True)
    role = Column(String(36), ForeignKey("cargos.id"), nullable=True)
    matricula = Column(String(50), nullable=True)
    phone = Column(String(64), nullable=True)
    pswd_last_updated = Column(DateTime, nullable=True)
    mfa_last_updated = Column(DateTime, nullable=True)
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)

    # Relationships (optional, won't fail if FK is invalid/null)
    orgao_data = relationship("Orgao", foreign_keys=[orgao])
    unidade_data = relationship("Unidade", foreign_keys=[unidade])
    cargo_data = relationship("Cargo", foreign_keys=[role])
    
    @property
    def is_active(self):
        return self.active == 'Y'
    
    def __repr__(self):
        return f"<SecUser(login={self.login}, email={self.email})>"
