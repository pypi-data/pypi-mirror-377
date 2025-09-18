
from http import HTTPStatus
from typing import Any, Union


class CommonException(Exception):
    code: int
    message: str
    detail: Union[Any, None]

    def __init__(
        self,
        code: int = HTTPStatus.BAD_REQUEST,
        message: str = "Bad Request",
        detail: Union[Any, None] = None
    ):
        self.code = code
        self.message = message
        self.detail = detail

    def __str__(self):
        return f"""
            code: {self.code}
            message: {self.message}
            detail: {self.detail}
            traceback: {self.__traceback__}
            """

    def to_dict(self):
        return {
            "code": self.code,
            "message": self.message,
            "detail": self.detail,
        }


class RecordNotFoundException(CommonException):
    def __init__(
        self,
        message: str = "Resource not found.",
        detail: Union[Any, None] = "not_found"
    ):
        super().__init__(HTTPStatus.NOT_FOUND, message, detail)

class ConflictException(CommonException):
    def __init__(
        self,
        message: str = "Conflict with existing resource.",
        detail: Union[Any, None] = None
    ):
        super().__init__(HTTPStatus.CONFLICT, message, detail)