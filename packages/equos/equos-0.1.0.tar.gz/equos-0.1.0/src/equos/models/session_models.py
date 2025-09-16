from dataclasses import dataclass
from typing import Optional, Union
from datetime import datetime

from pydantic import BaseModel

from equos.models.agent_models import CreateEquosAgentRequest, EquosAgent
from equos.models.avatar_models import CreateEquosAvatarRequest, EquosAvatar


@dataclass
class EquosParticipantIdentity:
    identity: str
    name: str


@dataclass
class EquosResourceId:
    id: str


class EquosServerUrl(BaseModel):
    serverUrl: str


@dataclass
class EquosSessionHost(EquosServerUrl):
    accessToken: str


@dataclass
class CreateEquosSessionRequest:
    name: str
    client: Optional[str]
    host: Optional[EquosSessionHost]
    agent: Optional[Union[EquosResourceId, CreateEquosAgentRequest]]
    avatar: Union[EquosResourceId, CreateEquosAvatarRequest]
    remoteAgentConnectingIdentity: Optional[EquosParticipantIdentity]
    consumerIdentity: Optional[EquosParticipantIdentity]


class EquosSession(BaseModel):
    id: str
    organizationId: str
    freemium: bool
    name: str
    provider: str
    client: Optional[str]
    status: str
    host: EquosServerUrl
    avatarId: str
    avatar: EquosAvatar
    agentId: Optional[str]
    agent: Optional[EquosAgent]
    startedAt: datetime
    endedAt: Optional[datetime]
    createdAt: datetime
    updatedAt: datetime


class CreateEquosSessionResponse(BaseModel):
    session: EquosSession
    consumerAccessToken: Optional[str]
    remoteAgentAccessToken: Optional[str]


class ListEquosSessionsResponse(BaseModel):
    skip: int
    take: int
    total: int
    sessions: list[EquosSession]
