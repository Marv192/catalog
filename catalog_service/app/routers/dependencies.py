import logging

from fastapi import Request

from app.utils.exceptions import PermissionDeniedError

logger = logging.getLogger(__name__)

def permission_required(permission_code: str):
    async def check_permission(request: Request):
        user = request.state.user
        permission_codes = user.get('permissions', [])

        if permission_code not in permission_codes:
            logger.warning("Missing permission", extra={"permission_code": permission_code})
            raise PermissionDeniedError(f"Missing permission {permission_code}")

        return True

    return check_permission
