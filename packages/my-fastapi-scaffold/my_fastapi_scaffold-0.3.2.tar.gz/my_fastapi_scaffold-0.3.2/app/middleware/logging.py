import logging
import time
import uuid
import json
from fastapi import Request
# (关键修复 1) 从 typing 模块导入 Callable 和 Awaitable
from typing import Callable, Awaitable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse

from app.core.logging_config import request_id_var, user_id_var
from app.exceptions.exceptions import AppException
from app.exceptions.error_codes import ErrorCode

logger = logging.getLogger(__name__)
api_traffic_logger = logging.getLogger("api_traffic")

PUBLIC_PATHS = {"/docs", "/openapi.json", "/favicon.ico"}


class LoggingMiddleware(BaseHTTPMiddleware):
    # (关键修复 2) 将 call_next 的类型提示更新为现代化的写法
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        start_time = time.time()
        request_id = str(uuid.uuid4())
        request_id_var.set(request_id)
        user_id = request.headers.get("x-user-id", "anonymous")
        user_id_var.set(user_id)

        action = "-"
        response = None

        try:
            if request.url.path not in PUBLIC_PATHS and not request.headers.get("x-user-id"):
                raise AppException(ErrorCode.MISSING_REQUIRED_HEADER, detail="请求中缺少必需的请求头: 'x-user-id'")

            req_body_bytes = await request.body()

            if "actions" in str(request.url.path) and req_body_bytes:
                try:
                    body_json = json.loads(req_body_bytes)
                    action = body_json.get("action", "unknown_action")
                except json.JSONDecodeError:
                    action = "invalid_json"

            async def receive():
                return {"type": "http.request", "body": req_body_bytes}

            new_request = Request(request.scope, receive=receive)

            response = await call_next(new_request)

        except AppException as exc:
            response = JSONResponse(
                status_code=exc.status_code,
                content={"error": exc.to_dict()}
            )
        except Exception as exc:
            error_code_info = ErrorCode.UNEXPECTED_ERROR
            logger.error(f"中间件中未处理的异常: {exc}", exc_info=True)
            response = JSONResponse(
                status_code=500,
                content={"error": error_code_info}
            )
        finally:
            process_time = (time.time() - start_time) * 1000
            status_code = response.status_code if response else 500
            client_ip = request.client.host if request.client else "unknown"

            log_message = (
                f'method="{request.method}" path="{request.url.path}" '
                f'action="{action}" status_code={status_code} '
                f'duration_ms={process_time:.2f} client_ip="{client_ip}"'
            )
            api_traffic_logger.info(log_message)

        return response