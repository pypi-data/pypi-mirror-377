from uuid import UUID

from .exceptions.sub_exceptions.not_found_exceptions import ProfileIDNotFoundException, UserIDNotFoundException
from .utils import decode_token
from .exceptions.sub_exceptions.forbidden_exceptions import AllOrganizationAccessForbiddenException


def get_all_info(token: str, public_key: bytes, jwt_algorithm: str) -> list[UUID]:
    """
    Decode jwt token and return payload dictionary.

    :param token: jwt token to decode
    :type token: str
    :param public_key: public key used to decode the token
    :type public_key: bytes
    :param jwt_algorithm: jwt algorithm used to decode the token
    :type jwt_algorithm: str
    :returns: payload dictionary
    :rtype: dict
    """
    payload = decode_token(token, public_key, jwt_algorithm)
    return payload.get("sub")


def get_organizations(token: str, public_key: bytes, jwt_algorithm: str) -> list[UUID]:
    """
    Decode jwt token and return a list of organization UUIDs from token payload dictionary.

    :param token: jwt token to decode
    :type token: str
    :param public_key: public key used to decode the token
    :type public_key: bytes
    :param jwt_algorithm: jwt algorithm used to decode the token
    :type jwt_algorithm: str
    :returns: a list of organization UUIDs from token payload dictionary
    :rtype: list[UUID]
    """
    payload = decode_token(token, public_key, jwt_algorithm)
    organizations_ids: list[UUID] = payload.get("sub").get("organizations")
    if not organizations_ids:
        raise AllOrganizationAccessForbiddenException
    return organizations_ids


def get_profile_id(token: str, public_key: bytes, jwt_algorithm: str) -> UUID:
    """
    Decode jwt token and return profile UUID from token payload dictionary.

    :param token: jwt token to decode
    :type token: str
    :param public_key: public key used to decode the token
    :type public_key: bytes
    :param jwt_algorithm: jwt algorithm used to decode the token
    :type jwt_algorithm: str
    :returns: a profile UUID from token payload dictionary
    :rtype: UUID
    """
    payload = decode_token(token, public_key, jwt_algorithm)
    profile_id = payload.get("sub").get("profile_id")
    if not profile_id:
        raise ProfileIDNotFoundException
    return profile_id


def get_user_id(token: str, public_key: bytes, jwt_algorithm: str) -> UUID:
    """
    Decode jwt token and return user UUID from token payload dictionary.

    :param token: jwt token to decode
    :type token: str
    :param public_key: public key used to decode the token
    :type public_key: bytes
    :param jwt_algorithm: jwt algorithm used to decode the token
    :type jwt_algorithm: str
    :returns: a user UUID from token payload dictionary
    :rtype: UUID
    """
    payload = decode_token(token, public_key, jwt_algorithm)
    user_id = payload.get("sub").get("user_id")
    if not user_id:
        raise UserIDNotFoundException
    return user_id


def get_user_permissions(token: str, public_key: bytes, jwt_algorithm: str) -> dict:
    """
    Decode jwt token and return user permissions from token payload dictionary.

    :param token: jwt token to decode
    :type token: str
    :param public_key: public key used to decode the token
    :type public_key: bytes
    :param jwt_algorithm: jwt algorithm used to decode the token
    :type jwt_algorithm: str
    :returns: user permissions from token payload dictionary
    :rtype: dict
    """
    payload = decode_token(token, public_key, jwt_algorithm)
    permissions = payload.get("sub").get("permissions")
    return permissions


def get_account_id(token: str, public_key: bytes, jwt_algorithm: str) -> UUID | None:
    """
    Decode jwt token and return account UUID from token payload dictionary.

    :param token: jwt token to decode
    :type token: str
    :param public_key: public key used to decode the token
    :type public_key: bytes
    :param jwt_algorithm: jwt algorithm used to decode the token
    :type jwt_algorithm: str
    :returns: account UUID from token payload dictionary
    :rtype: UUID
    """
    payload = decode_token(token, public_key, jwt_algorithm)
    account_id = payload.get("sub").get("account_id")
    return account_id
