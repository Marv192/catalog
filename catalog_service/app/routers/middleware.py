from fastapi import Request, status, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.tokens import decode_token


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.public_paths = [
            '/docs',
            '/openapi.json'
        ]

    async def dispatch(self, request: Request, call_next):
        if any(request.url.path.startswith(path) for path in self.public_paths):
            return await call_next(request)

        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Invalid or missing Authorization Header')

        token = auth_header.split(' ')[1]

        try:
            payload = decode_token(token)
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        request.state.user = payload

        return await call_next(request)




