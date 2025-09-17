import logging
import time
import uuid
import json
from fastapi import Request
from typing import Callable, Awaitable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse

from app.core.logging_config import request_id_var, user_id_var, api_action_var
from app.exceptions.exceptions import AppException
from app.exceptions.error_codes import ErrorCode

logger = logging.getLogger(__name__)
api_traffic_logger = logging.getLogger("api_traffic")

PUBLIC_PATHS = {"/docs", "/openapi.json", "/favicon.ico"}


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        start_time = time.time()
        request_id = str(uuid.uuid4())

        # 设置日志上下文变量
        request_id_var.set(request_id)
        user_id = request.headers.get("x-user-id", "anonymous")
        user_id_var.set(user_id)

        action = "-"  # 默认为'-'
        status_code = 500  # 默认状态码为500，以防万一

        try:
            # --- 中间件自身逻辑 ---
            if request.url.path not in PUBLIC_PATHS and not request.headers.get("x-user-id"):
                raise AppException(ErrorCode.MISSING_REQUIRED_HEADER, name="x-user-id")

            req_body_bytes = await request.body()

            if "actions" in str(request.url.path) and req_body_bytes:
                try:
                    body_json = json.loads(req_body_bytes)
                    action = body_json.get("action", "unknown_action")
                    api_action_var.set(action)
                except json.JSONDecodeError:
                    action = "invalid_json"

            async def receive():
                return {"type": "http.request", "body": req_body_bytes}

            new_request = Request(request.scope, receive=receive)

            # --- 核心逻辑 ---
            # 将请求传递给后续的应用层
            response = await call_next(new_request)
            # 如果成功返回，从响应中获取状态码
            status_code = response.status_code
            return response

        except Exception as exc:
            # --- 关键改动 ---
            # 捕获所有异常，仅用于确定正确的状态码
            if isinstance(exc, AppException):
                # 如果是我们的自定义业务异常，从中获取状态码
                status_code = exc.status_code

            # 重新抛出异常，让在main.py中注册的全局异常处理器来生成最终的响应体
            raise exc

        finally:
            # 无论成功还是发生异常，finally 块都会执行
            process_time = (time.time() - start_time) * 1000
            client_ip = request.client.host if request.client else "unknown"

            log_message = (
                f'method="{request.method}" path="{request.url.path}" '
                f'action="{action}" status_code={status_code} '
                f'duration_ms={process_time:.2f} client_ip="{client_ip}"'
            )
            api_traffic_logger.info(log_message)