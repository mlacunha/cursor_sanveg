from sqlalchemy import Column, String
from app.config.database import Base


class SecSetting(Base):
    __tablename__ = "sec_settings"

    set_name = Column(String(255), primary_key=True, index=True)
    set_value = Column(String(255), nullable=True)
