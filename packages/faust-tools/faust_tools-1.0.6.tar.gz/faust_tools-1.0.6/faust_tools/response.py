from http import HTTPStatus


class Response:
    id: str | None
    status: HTTPStatus
    detail: dict | None

    def __init__(
        self,
        *,
        id: str | None = None,
        status: HTTPStatus = HTTPStatus.OK,
        detail: dict | None = None,
    ):
        self.id = id
        self.status = status
        self.detail = detail
