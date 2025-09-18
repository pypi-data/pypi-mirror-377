import jwt

from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from starlette.requests import Request

from .exceptions.sub_exceptions.unauthorized_exceptions import TokenExpiredException, IncorrectTokenFormatException, \
    UserUnauthorizedException


def get_token_from_request(request: Request) -> str:
    """
    Extract and return token from request headers.

    :param request: an http request
    :type request: Request
    :returns: token
    :rtype: str
    """
    if not request.headers.get('Authorization'):
        raise UserUnauthorizedException
    try:
        token = request.headers.get('Authorization').split(" ")[1]
        return token
    except Exception as e:
        # Если IndexError, скорее всего токен передан без префикса "Bearer "
        print(f"Ошибка в методе get_token.\n"
              f"Тип исключения: {type(e).__name__}\nСообщение: {str(e)}\n"
              f"Переданный токен: {request.headers.get('Authorization')}")
        raise IncorrectTokenFormatException


def decode_token(token: str, public_key: bytes, jwt_algorithm: str) -> dict:
    """
    Decode jwt token and return payload dictionary.

    :param token: jwt token to decode
    :type token: str
    :param public_key: public key used to decode the token
    :type public_key: bytes
    :param jwt_algorithm: jwt algorithm used to decode the token
    :type jwt_algorithm: str
    :returns: payload from the token
    :rtype: dict
    """
    try:
        payload = jwt.decode(
            token, public_key, jwt_algorithm
        )
        return payload
    except ExpiredSignatureError:
        raise TokenExpiredException
    except InvalidTokenError as e:
        print(e)
        raise IncorrectTokenFormatException


def validate_token(token: str, public_key: bytes, jwt_algorithm: str):
    """
    Validate jwt token. Nothing is returned in case of successful validation. An exception is thrown otherwise.

    :param token: jwt token
    :type token: str
    :param public_key: public key
    :type public_key: bytes
    :param jwt_algorithm: jwt algorithm
    :type jwt_algorithm: str
    """
    decode_token(token=token, public_key=public_key, jwt_algorithm=jwt_algorithm)
