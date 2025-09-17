class SuccessCode:
    """
    一个用于集中管理 API 成功响应码和描述的类。
    """
    OK = {
        "code": "OK",
        "message": "操作成功。",
        "status_code": 200
    }
    CREATED = {
        "code": "CREATED",
        "message": "资源创建成功。",
        "status_code": 201
    }
    ACCEPTED = {
        "code": "ACCEPTED",
        "message": "请求已被接受，正在处理中。",
        "status_code": 202
    }


class ErrorCode:
    """
    一个用于集中管理 API 错误码和描述的类。
    这是整个应用业务错误的“唯一事实来源”。
    """
    # =================================================================
    # 1. 通用和请求错误 (Generic & Request Errors) - 4xx
    # =================================================================
    BAD_REQUEST = {
        "code": "BAD_REQUEST",
        "message": "请求格式错误或无效。",
        "status_code": 400
    }
    VALIDATION_ERROR = {
        "code": "VALIDATION_ERROR",
        "message": "一个或多个字段未能通过验证。",
        "status_code": 400
    }
    MISSING_REQUIRED_FIELD = {
        "code": "MISSING_REQUIRED_FIELD",
        "message": "请求体中缺少必需的字段：'{name}'。",
        "status_code": 400
    }
    MISSING_REQUIRED_HEADER = {
        "code": "MISSING_REQUIRED_HEADER",
        "message": "请求中缺少必需的请求头：'{name}'。",
        "status_code": 400
    }
    INVALID_INPUT_FORMAT = {
        "code": "INVALID_INPUT_FORMAT",
        "message": "输入数据的格式无效。(例如：无效的JSON)",
        "status_code": 400
    }
    UNSUPPORTED_MEDIA_TYPE = {
        "code": "UNSUPPORTED_MEDIA_TYPE",
        "message": "不支持所提供的媒体类型。",
        "status_code": 415
    }

    # =================================================================
    # 2. 认证与授权错误 (Authentication & Authorization Errors) - 401, 403
    # =================================================================
    AUTHENTICATION_REQUIRED = {
        "code": "AUTHENTICATION_REQUIRED",
        "message": "访问此资源需要提供认证凭据。",
        "status_code": 401
    }
    INVALID_CREDENTIALS = {
        "code": "INVALID_CREDENTIALS",
        "message": "提供的凭据无效（例如：用户名或密码错误）。",
        "status_code": 401
    }
    INVALID_TOKEN = {
        "code": "INVALID_TOKEN",
        "message": "提供的认证令牌无效、格式错误或已过期。",
        "status_code": 401
    }
    PERMISSION_DENIED = {
        "code": "PERMISSION_DENIED",
        "message": "您没有权限执行此操作。",
        "status_code": 403
    }

    # =================================================================
    # 3. 资源相关错误 (Resource Errors) - 404, 409
    # =================================================================
    RESOURCE_NOT_FOUND = {
        "code": "RESOURCE_NOT_FOUND",
        "message": "请求的资源未找到。",
        "status_code": 404
    }
    USER_NOT_FOUND = {
        "code": "USER_NOT_FOUND",
        "message": "未找到具有指定标识符的用户。",
        "status_code": 404
    }
    DUPLICATE_RESOURCE = {
        "code": "DUPLICATE_RESOURCE",
        "message": "具有相同标识符的资源已存在。",
        "status_code": 409
    }

    # =================================================================
    # 4. 服务端错误 (Server Errors) - 5xx
    # =================================================================
    UNEXPECTED_ERROR = {
        "code": "UNEXPECTED_ERROR",
        "message": "服务器发生意外错误。",
        "status_code": 500
    }
    DATABASE_ERROR = {
        "code": "DATABASE_ERROR",
        "message": "处理请求时发生数据库错误。",
        "status_code": 500
    }
    EXTERNAL_SERVICE_UNAVAILABLE = {
        "code": "EXTERNAL_SERVICE_UNAVAILABLE",
        "message": "此操作所需的外部服务当前不可用。",
        "status_code": 503
    }
    # --- (新增) 与我们定义的 CacheServiceUnavailableError 异常保持同步 ---
    CACHE_SERVICE_UNAVAILABLE = {
        "code": "CACHE_SERVICE_UNAVAILABLE",
        "message": "缓存服务（如 Redis）当前不可用。",
        "status_code": 503
    }




    # =================================================================
    # 5. 速率限制错误 (Rate Limiting Errors) - 429
    # =================================================================
    RATE_LIMIT_EXCEEDED = {
        "code": "RATE_LIMIT_EXCEEDED",
        "message": "您已超出请求速率限制。",
        "status_code": 429
    }