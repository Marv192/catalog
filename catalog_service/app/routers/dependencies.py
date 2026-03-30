from fastapi import Request

from app.utils.exceptions import PermissionDeniedError


def permission_required(permission_code: str):
    async def check_permission(request: Request):
        user = request.state.user
        permission_codes = user.get('permissions', [])

        if permission_code not in permission_codes:
            raise PermissionDeniedError(f"Missing permission {permission_code}")

        return True

    return check_permission
