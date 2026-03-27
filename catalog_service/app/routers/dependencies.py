from fastapi.params import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.utils.exceptions import PermissionDeniedError
from app.utils.tokens import decode_token

security = HTTPBearer()

def permission_required(permission_code: str):
    async def check_permission(credentials: HTTPAuthorizationCredentials = Depends(security)):
        token = credentials.credentials
        payload = decode_token(token)
        permission_codes = payload.get('permissions', [])

        if permission_code not in permission_codes:
            raise PermissionDeniedError(f"Missing permission {permission_code}")

        return True
    return check_permission