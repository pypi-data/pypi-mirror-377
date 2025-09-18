from ..main_exceptions import UnauthorizedException


class IncorrectTokenFormatException(UnauthorizedException):
    def __init__(self):
        super().__init__(code="TOKEN_INCORRECT", message="Неверный формат токена.")


class UserUnauthorizedException(UnauthorizedException):
    def __init__(self):
        super().__init__(message="Пользователь не авторизован.")


class TokenExpiredException(UnauthorizedException):
    def __init__(self):
        super().__init__(code="TOKEN_EXPIRED", message="Токен истек.")
