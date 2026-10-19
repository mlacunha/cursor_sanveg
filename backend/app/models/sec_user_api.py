from sqlalchemy import Column, String
from app.config.database import Base


class SecUserApi(Base):
    __tablename__ = "sec_users_api"

    login = Column(String(255), primary_key=True, index=True)
    pswd = Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    active = Column(String(1), nullable=True, default='Y')
