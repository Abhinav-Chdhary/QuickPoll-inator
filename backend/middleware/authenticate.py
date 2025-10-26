# middleware/authenticate.py
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException, status
from typing import Callable
from utils.auth import decode_access_token

PUBLIC_PATHS = {
    "/",
    "/user/register",
    "/user/login",
}
PUBLIC_PREFIXES = (
    "/docs",
    "/redoc",
    "/static",
)


class AuthenticateMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        path = request.url.path

        # Allow public paths and prefixes
        if path in PUBLIC_PATHS or any(path.startswith(p) for p in PUBLIC_PREFIXES):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth_header.split(" ", 1)[1].strip()
        payload = decode_access_token(token)  # raises 401 if invalid/expired

        # Make token payload available to route handlers
        request.state.user = payload

        return await call_next(request)
