import jwt

from app.config import JWT_SECRET, JWT_ALGORITHM
from app.utils.exceptions import TokenExpiredError, InvalidTokenError


def decode_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError
    except jwt.InvalidTokenError:
        raise InvalidTokenError

