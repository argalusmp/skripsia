from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

class RoleMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Contoh validasi role
        if request.url.path.startswith("/knowledge") and request.method == "DELETE":
            user_role = request.headers.get("X-User-Role")
            if user_role != "admin":
                return JSONResponse({"detail": "Access forbidden"}, status_code=403)
        return await call_next(request)