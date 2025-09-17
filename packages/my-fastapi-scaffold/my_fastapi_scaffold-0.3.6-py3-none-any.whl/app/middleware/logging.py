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
            # 1. (可选) 检查必要的请求头。如果失败，它将作为AppException被全局处理器捕获
            if request.url.path not in PUBLIC_PATHS and not request.headers.get("x-user-id"):
                raise AppException(ErrorCode.MISSING_REQUIRED_HEADER, name="x-user-id")

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

            # --- 核心改动 ---
            # 直接调用 call_next，不在此处捕获任何异常。
            # 让所有异常（无论是 AppException 还是其他 Exception）
            # 都自由地“冒泡”出去，由 FastAPI 的异常处理机制接管。
            response = await call_next(new_request)

        finally:
            # 无论成功还是失败（即使发生异常），finally 块都会执行
            process_time = (time.time() - start_time) * 1000

            # 关键：如果 response 对象尚未创建（因为 call_next 抛出异常），
            # 我们无法知道最终状态码，但依然可以记录请求本身。
            # FastAPI 的全局处理器会确保客户端收到正确的响应。
            status_code = response.status_code if response else 500  # 假设未成功则为500

            client_ip = request.client.host if request.client else "unknown"

            log_message = (
                f'method="{request.method}" path="{request.url.path}" '
                f'action="{action}" status_code={status_code} '
                f'duration_ms={process_time:.2f} client_ip="{client_ip}"'
            )
            api_traffic_logger.info(log_message)

        return response