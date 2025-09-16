from typing import Optional
from equos.utils.http_utils import HttpUtils

from equos.models.error_models import EquosException

from equos.models.avatar_models import (
    CreateEquosAvatarRequest,
    EquosAvatar,
    ListEquosAvatarsResponse,
)


class EquosAvatarApi:
    def __init__(self, http: HttpUtils):
        self.http = http

    def create(self, *, data: CreateEquosAvatarRequest) -> EquosAvatar:
        res = self.http.post("/avatars", data)

        if res is None:
            raise EquosException("Create avatar response is None")

        return EquosAvatar.model_validate(res)

    def list(
        self, *, skip: int = 0, take: int = 10, client: Optional[str] = None
    ) -> ListEquosAvatarsResponse:
        path = f"/avatars?skip={skip}&take={take}"

        if client:
            path += f"&client={client}"

        res = self.http.get(path)

        if res is None:
            raise EquosException("List avatars response is None")

        return ListEquosAvatarsResponse.model_validate(res)

    def get(self, *, id: str) -> Optional[EquosAvatar]:
        res = self.http.get(f"/avatars/{id}")

        if res is None:
            return None

        return EquosAvatar.model_validate(res)
