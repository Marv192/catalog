import logging

import jwt

from app.config import settings
from app.utils.exceptions import TokenExpiredError, InvalidTokenError


logger = logging.getLogger(__name__)

def decode_token(token: str):
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Decode token failed: token expired")
        raise TokenExpiredError
    except jwt.InvalidTokenError:
        logger.warning("Decode token failed: invalid token")
        raise InvalidTokenError

