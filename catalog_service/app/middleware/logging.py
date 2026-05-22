import contextvars
import logging
import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

request_id_ctx: contextvars.ContextVar[str | None] = contextvars.ContextVar("request_id", default=None)


class LoggingMiddleware(BaseHTTPMiddleware):
    SKIP_LOGGING_PATHS = {"/metrics"}

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.SKIP_LOGGING_PATHS:
            return await call_next(request)

        request_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))
        request.state.request_id = request_id
        request_id_ctx.set(request_id)

        start_time = time.perf_counter()
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"

        try:
            response = await call_next(request)

            duration_ms = (time.perf_counter() - start_time) * 1000
            user_id = getattr(request.state, "user_id", None)

            logger.info("HTTP request completed", extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "client_ip": client_ip,
                "duration_ms": round(duration_ms, 2),
                "status_code": response.status_code,
                "user_id": user_id,
            })
            return response

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            status_code = getattr(e, "status_code", 500)

            logger.exception("HTTP request failed", extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration_ms": round(duration_ms, 2),
                "client_ip": client_ip,
                "user_id": getattr(request.state, "user_id", None),
                "error_type": type(e).__name__,
            })
            raise