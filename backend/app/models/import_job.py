from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from app.config.database import Base


class ImportJob(Base):
    __tablename__ = "municipios_import_jobs"

    id = Column(Integer, primary_key=True, index=True)
    estado_sigla = Column(String(10), nullable=True)
    status = Column(String(20), nullable=False, default="pending")
    force_reload = Column(Boolean, nullable=False, default=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    total = Column(Integer, nullable=True)
    existing = Column(Integer, nullable=True)
    new = Column(Integer, nullable=True)
    error = Column(Text, nullable=True)
