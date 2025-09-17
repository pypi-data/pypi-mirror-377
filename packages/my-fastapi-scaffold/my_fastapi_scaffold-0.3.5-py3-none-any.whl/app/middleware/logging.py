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

        response = None
        action = "-"  # 默认为'-'

        try:
            # --- 中间件自身逻辑 ---
            # 1. 检查必要的请求头
            if request.url.path not in PUBLIC_PATHS and not request.headers.get("x-user-id"):
                # 注意：这里抛出的异常会被下面的 except Exception 捕获，并最终返回500
                # 这是一个设计选择，也可以直接返回一个JSONResponse
                raise AppException(ErrorCode.MISSING_REQUIRED_HEADER, detail="请求中缺少必需的请求头: 'x-user-id'")

            # 2. 安全地读取和重用请求体
            req_body_bytes = await request.body()

            # 3. 尝试从请求体中解析 action，用于日志记录
            if "actions" in str(request.url.path) and req_body_bytes:
                try:
                    body_json = json.loads(req_body_bytes)
                    action = body_json.get("action", "unknown_action")
                    api_action_var.set(action)  # 将 action 存入上下文
                except json.JSONDecodeError:
                    action = "invalid_json"

            async def receive():
                return {"type": "http.request", "body": req_body_bytes}

            new_request = Request(request.scope, receive=receive)

            # --- 关键改动 ---
            # 将请求传递给后续的应用（路由、依赖项等）
            # 我们不再在这里用 try...except AppException 来捕获业务异常
            # 让异常自由地“冒泡”出去，由在 main.py 中注册的全局异常处理器来接管
            response = await call_next(new_request)

        except Exception as exc:
            # 这个 except 块现在只作为最后的“安全网”
            # 用于捕获在中间件自身逻辑中或应用中未被处理的、意料之外的严重错误
            logger.error(f"中间件捕获到未处理的异常: {exc}", exc_info=True)

            # 当发生未知错误时，返回一个标准的 500 响应
            error_code_info = ErrorCode.UNEXPECTED_ERROR
            response = JSONResponse(
                status_code=error_code_info.get("status_code", 500),
                content={
                    "code": error_code_info.get("code"),
                    "message": error_code_info.get("message"),
                    "details": None
                }
            )
        finally:
            # 无论成功还是失败，finally 块都会执行，确保API流量日志总是被记录
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