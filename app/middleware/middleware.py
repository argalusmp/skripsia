from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

class RoleMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Ambil role pengguna dari header
        user_role = request.headers.get("X-User-Role")

        if request.url.path.startswith("/knowledge"):
            if request.method == "DELETE" and user_role != "admin":
                return JSONResponse({"detail": "Access forbidden: Admin role required"}, status_code=403)

            if request.method == "POST" and user_role != "admin":
                return JSONResponse({"detail": "Access forbidden: Admin role required"}, status_code=403)

        # Jika tidak ada pembatasan, lanjutkan ke handler berikutnya
        return await call_next(request)