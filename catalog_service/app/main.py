import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Security, Request, status
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse

from app.models import engine
from app.routers.categories import categories
from app.routers.middleware import AuthMiddleware
from app.routers.products import products
from app.utils.exceptions import PermissionDeniedError, TokenExpiredError, InvalidTokenError

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await engine.connect()
        logger.info("Database connected")
    except Exception as e:
        logger.error(f"Database connection error: {e}")
    yield
    try:
        engine.disconnect()
    except Exception as e:
        logger.error(f"Database disconnect error: {e}")


security = HTTPBearer()

app = FastAPI(lifespan=lifespan, title="Catalog Service")


@app.exception_handler(PermissionDeniedError)
async def permission_denied_handler(request: Request, exc: PermissionDeniedError):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "error": "Permission denied",
            "detail": str(exc)
        }
    )


@app.exception_handler(TokenExpiredError)
async def token_expired_handler(request: Request, exc: TokenExpiredError):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "error": "Token expired",
            "detail": str(exc)
        }
    )


@app.exception_handler(InvalidTokenError)
async def invalid_token_handler(request: Request, exc: InvalidTokenError):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "error": "Invalid token",
            "detail": str(exc)
        }
    )


app.add_middleware(AuthMiddleware)
app.include_router(categories, prefix="/categories", tags=["categories"], dependencies=[Security(security)])
app.include_router(products, prefix="/products", tags=["products"], dependencies=[Security(security)])
