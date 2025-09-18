from ..main_exceptions import NotFoundException


class ProfileIDNotFoundException(NotFoundException):
    def __init__(self):
        super().__init__(message="Токен не содержит айди профиля.")


class UserIDNotFoundException(NotFoundException):
    def __init__(self):
        super().__init__(message="Токен не содержит айди пользователя.")
