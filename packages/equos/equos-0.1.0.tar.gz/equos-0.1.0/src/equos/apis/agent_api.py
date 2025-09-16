from typing import Optional
from equos.utils.http_utils import HttpUtils

from equos.models.error_models import EquosException

from equos.models.agent_models import (
    CreateEquosAgentRequest,
    EquosAgent,
    ListEquosAgentsResponse,
)


class EquosAgentApi:
    def __init__(self, http: HttpUtils):
        self.http = http

    def create(self, *, data: CreateEquosAgentRequest) -> EquosAgent:
        res = self.http.post("/agents", data)

        if res is None:
            raise EquosException("Create agent response is None")

        return EquosAgent.model_validate(res)

    def list(
        self, *, skip: int = 0, take: int = 10, client: Optional[str] = None
    ) -> ListEquosAgentsResponse:
        path = f"/agents?skip={skip}&take={take}"

        if client:
            path += f"&client={client}"

        res = self.http.get(path)

        if res is None:
            raise EquosException("List agents response is None")

        return ListEquosAgentsResponse.model_validate(res)

    def get(self, *, id: str) -> Optional[EquosAgent]:
        res = self.http.get(f"/agents/{id}")

        if res is None:
            return None

        return EquosAgent.model_validate(res)
