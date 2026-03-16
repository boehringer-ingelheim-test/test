import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON
from app.core.database import Base


class Provision(Base):
    __tablename__ = "provisions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, unique=True)        # user or group name
    owner = Column(String, nullable=False)                    # requesting user / team
    tshirt_size = Column(String, nullable=False, default="medium")  # small|medium|large
    status = Column(String, nullable=False, default="pending")      # pending|provisioning|active|failed|destroyed
    terraform_workspace = Column(String, nullable=True)
    outputs = Column(JSON, nullable=True)                     # Terraform outputs stored as JSON
    error = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
