from datetime import datetime
from typing import Optional

from pydantic import BaseModel


from equos.models.agent_models import CreateEquosAgentRequest, EquosAgent


class CreateEquosAvatarRequest(BaseModel):
    identity: str
    name: str
    refImage: str
    client: Optional[str] = None
    agentId: Optional[str] = None
    agent: Optional[CreateEquosAgentRequest] = None


class EquosAvatar(BaseModel):
    id: str
    organizationId: str
    identity: str
    name: str
    client: Optional[str] = None
    thumbnailUrl: str
    createdAt: datetime
    updatedAt: datetime

    agentId: Optional[str] = None
    agent: Optional[EquosAgent] = None


class ListEquosAvatarsResponse(BaseModel):
    skip: int
    take: int
    total: int
    avatars: list[EquosAvatar]
