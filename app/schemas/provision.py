from datetime import datetime
from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


TshirtSize = Literal["small", "medium", "large"]
ProvisionStatus = Literal["pending", "provisioning", "active", "failed", "destroyed"]


class ProvisionCreate(BaseModel):
    name: str = Field(..., description="Unique identifier for the user/group (used as workspace name)")
    owner: str = Field(..., description="Requesting user or team")
    tshirt_size: TshirtSize = Field("medium", description="Resource size: small | medium | large")


class ProvisionResponse(BaseModel):
    id: str
    name: str
    owner: str
    tshirt_size: str
    status: ProvisionStatus
    terraform_workspace: Optional[str] = None
    outputs: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProvisionListResponse(BaseModel):
    total: int
    items: list[ProvisionResponse]
