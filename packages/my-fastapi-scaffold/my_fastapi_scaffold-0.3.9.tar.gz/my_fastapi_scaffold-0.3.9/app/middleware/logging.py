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

logger = logging.getLogger("app.middleware")  # 使用专属 logger 名称
api_traffic_logger = logging.getLogger("api_traffic")

PUBLIC_PATHS = {"/docs", "/openapi.json", "/favicon.ico"}


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        start_time = time.time()
        request_id = str(uuid.uuid4())

        request_id_var.set(request_id)
        user_id = request.headers.get("x-user-id", "anonymous")
        user_id_var.set(user_id)

        response = None
        action = "-"

        try:
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

            response = await call_next(new_request)

        except AppException as exc:
            # 捕获我们自定义的业务异常，并生成与全局处理器格式一致的“扁平”响应
            error_content = exc.to_dict()
            response = JSONResponse(
                status_code=exc.status_code,
                content={
                    "code": error_content.get("code"),
                    "message": error_content.get("message"),
                    "details": getattr(exc, 'details', None)
                }
            )
            # 同时，将这个业务异常作为“警告”记录下来
            logger.warning(
                f"业务异常被中间件处理: Code={exc.code}, Message={exc.detail}"
            )

        except Exception as exc:
            # 捕获所有其他未知异常，记录为错误，并返回标准的 500 响应
            logger.error(f"中间件捕获到未处理的异常: {exc}", exc_info=True)
            error_code_info = ErrorCode.UNEXPECTED_ERROR
            response = JSONResponse(
                status_code=error_code_info.get("status_code", 500),
                content={
                    "code": error_code_info.get("code"),
                    "message": error_code_info.get("message"),
                    "details": str(exc)  # 在 details 中提供一些原始错误信息
                }
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