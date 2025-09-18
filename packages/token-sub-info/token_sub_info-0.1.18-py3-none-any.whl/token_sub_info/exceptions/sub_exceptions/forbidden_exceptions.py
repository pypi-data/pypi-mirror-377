from ..main_exceptions import ForbiddenException


class AllOrganizationAccessForbiddenException(ForbiddenException):
    def __init__(self):
        super().__init__(code="FORBIDDEN", message="Пользователь не имеет доступа ни к одной из организаций.")
