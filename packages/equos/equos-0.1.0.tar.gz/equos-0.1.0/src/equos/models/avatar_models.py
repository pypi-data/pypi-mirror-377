from datetime import datetime
from typing import Optional
from dataclasses import dataclass

from pydantic import BaseModel


from equos.models.agent_models import CreateEquosAgentRequest, EquosAgent


@dataclass
class CreateEquosAvatarRequest:
    identity: str
    name: str
    refImage: str
    client: Optional[str]
    agentId: Optional[str]
    agent: Optional[CreateEquosAgentRequest]


class EquosAvatar(BaseModel):
    id: str
    organizationId: str
    identity: str
    name: str
    client: Optional[str]
    thumbnailUrl: str
    createdAt: datetime
    updatedAt: datetime

    agentId: Optional[str]
    agent: Optional[EquosAgent]


class ListEquosAvatarsResponse(BaseModel):
    skip: int
    take: int
    total: int
    avatars: list[EquosAvatar]
