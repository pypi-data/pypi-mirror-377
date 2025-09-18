from typing import Dict, Any

# 导入你的 ErrorCode，确保路径正确
from app.exceptions.error_codes import ErrorCode


# 1. --- 统一的、功能强大的基础异常类 ---
class AppException(Exception):
    """
    所有自定义业务异常的基类。
    集成了 ErrorCode，提供了灵活的消息格式化功能。
    """

    def __init__(
        self,
        error_code: Dict[str, Any],    # 必须传入一个来自 ErrorCode 的字典
        detail: str | None = None,     # 可选，用于覆盖默认消息的自定义详情
        **kwargs                       # 用于格式化 message 模板中的占位符，如 {name}
    ):
        # 从 ErrorCode 字典中获取基础信息
        self.status_code = error_code.get("status_code", 500)
        self.code = error_code.get("code", "UNEXPECTED_ERROR")
        message_template = error_code.get("message", "服务器发生未知错误。")

        # 优先使用传入的 detail，否则使用模板和 kwargs 格式化消息
        self.detail = detail or message_template.format(**kwargs)

        super().__init__(self.detail)

    def to_dict(self) -> dict:
        """将异常安全地转换为一个字典，用于 FastAPI 的 JSON 响应。"""
        return {
            "code": self.code,
            "message": self.detail
        }


# 2. --- 基于 AppException 的具体业务异常 ---

# =================================================================
# 通用和请求错误 (Generic & Request Errors)
# =================================================================
class MissingHeaderException(AppException):
    """当请求中缺少必要的头信息时抛出。"""
    def __init__(self, name: str, detail: str | None = None):
        super().__init__(
            error_code=ErrorCode.MISSING_REQUIRED_HEADER,
            detail=detail,
            name=name  # 传递 'name' 关键字参数以格式化消息
        )

class MissingFieldException(AppException):
    """当请求体中缺少必要的字段时抛出。"""
    def __init__(self, name: str, detail: str | None = None):
        super().__init__(
            error_code=ErrorCode.MISSING_REQUIRED_FIELD,
            detail=detail,
            name=name
        )

# =================================================================
# 认证与授权错误 (Authentication & Authorization Errors)
# =================================================================
class InvalidCredentialsException(AppException):
    """当提供的认证信息无效时抛出 (例如，密码错误)。"""
    def __init__(self, detail: str | None = None):
        super().__init__(
            error_code=ErrorCode.INVALID_CREDENTIALS,
            detail=detail
        )

class PermissionDeniedException(AppException):
    """当用户认证成功但权限不足以执行操作时抛出。"""
    def __init__(self, detail: str | None = None):
        super().__init__(
            error_code=ErrorCode.PERMISSION_DENIED,
            detail=detail
        )


# =================================================================
# 资源相关错误 (Resource Errors)
# =================================================================
class ResourceNotFoundException(AppException):
    """当在数据库中找不到特定资源时抛出。"""
    def __init__(self, detail: str | None = None):
        super().__init__(
            error_code=ErrorCode.RESOURCE_NOT_FOUND,
            detail=detail
        )

class DuplicateResourceException(AppException):
    """当尝试创建已存在的资源时抛出 (例如，邮箱已注册)。"""
    def __init__(self, detail: str | None = None):
        super().__init__(
            error_code=ErrorCode.DUPLICATE_RESOURCE,
            detail=detail
        )

# =================================================================
# 服务端与外部服务错误 (Server & External Service Errors)
# =================================================================
# ⭐ 在此补充我们之前定义的 Cache 异常，并让它们继承自新的 AppException
class CacheConnectionError(AppException):
    """当无法初始化或连接到缓存服务（如 Redis）时抛出。"""
    def __init__(self, detail: str | None = None):
        super().__init__(
            error_code=ErrorCode.EXTERNAL_SERVICE_UNAVAILABLE, # 链接到对应的错误码
            detail=detail  # 提供一个更具体的默认消息
        )

class CacheServiceUnavailableError(AppException):
    """当在请求处理过程中，发现缓存服务不可用时抛出。"""
    def __init__(self, detail: str | None = None):
        super().__init__(
            error_code=ErrorCode.CACHE_SERVICE_UNAVAILABLE, # 链接到对应的错误码
            status_code=503,
            detail=detail
        )