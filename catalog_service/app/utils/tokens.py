import jwt

from app.config import settings
from app.utils.exceptions import TokenExpiredError, InvalidTokenError


def decode_token(token: str):
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError
    except jwt.InvalidTokenError:
        raise InvalidTokenError

