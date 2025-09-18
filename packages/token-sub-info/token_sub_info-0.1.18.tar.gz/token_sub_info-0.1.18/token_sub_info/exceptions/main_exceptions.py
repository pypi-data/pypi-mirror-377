from fastapi import status

from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder

from ..schemas.schemas import ResponseDetail


class ServiceException(HTTPException):
    def __init__(self, status_code: int = 500, code: str = None, message: str = None):
        self.status_code = status_code
        self._detail = ResponseDetail(code=code, message=message)
        super().__init__(status_code=self.status_code, detail=jsonable_encoder(self._detail))


class UnauthorizedException(ServiceException):
    def __init__(self, code="UNAUTHORIZED", message="Клиент не идентифицирован."):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, code=code, message=message)


class ForbiddenException(ServiceException):
    def __init__(self, code="FORBIDDEN", message="Доступ запрещен."):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, code=code, message=message)


class NotFoundException(ServiceException):
    def __init__(self, code="NOT_FOUND", message="Объект не найден."):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, code=code, message=message)
