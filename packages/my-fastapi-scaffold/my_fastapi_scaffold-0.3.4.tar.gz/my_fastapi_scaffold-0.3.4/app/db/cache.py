# app/db/cache.py (新文件)
import redis
import redis.asyncio as aioredis
from redis.asyncio.connection import ConnectionPool
from app.core.config import settings
import logging
from app.exceptions.exceptions import CacheConnectionError, CacheServiceUnavailableError


user_activity_logger = logging.getLogger("user_activity")

# 我们将创建一个全局连接池，由 lifespan 管理
redis_pool: ConnectionPool | None = None


def get_redis_url() -> str:
    """构建用于 aioredis 连接池的 URL。"""
    # redis://[:password@]host:port/db
    password = f":{settings.REDIS_PASSWORD}@" if settings.REDIS_PASSWORD else ""
    return f"redis://{password}{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"


async def init_redis_pool():
    """在应用启动时初始化 Redis 连接池"""
    global redis_pool
    if redis_pool is None:
        redis_url = get_redis_url()
        user_activity_logger.info(
            f"初始化 Redis 连接池: redis://...:{settings.REDIS_PORT}/{settings.REDIS_DB}")
        try:
            redis_pool = aioredis.ConnectionPool.from_url(
                redis_url,
                decode_responses=True  # 关键：自动将 redis 的 bytes 解码为 str
            )
            # 测试连接
            async with aioredis.Redis(connection_pool=redis_pool) as redis:
                await redis.ping()
            user_activity_logger.info("Redis 池初始化成功。")
        except Exception as e:
            user_activity_logger.error(f"无法初始化 Redis 池: {e}", exc_info=True)
            redis_pool = None  # 保持 None 以便重试或失败
            raise CacheConnectionError(f"无法连接到 Redis {redis_url}") from e


async def close_redis_pool():
    """在应用关闭时关闭 Redis 连接池"""
    global redis_pool
    if redis_pool:
        user_activity_logger.info("正在关闭 Redis 连接池...")
        await redis_pool.disconnect()
        redis_pool = None


async def get_redis():
    """
    FastAPI 依赖项：从池中获取一个单独的 Redis 连接。
    """
    if redis_pool is None:
        # 如果连接池不存在，说明应用启动时初始化失败，这是一个严重错误。
        # 我们应该直接让请求失败，而不是尝试在这里修复。
        raise CacheServiceUnavailableError("Redis 连接池不可用。请检查服务器启动日志。")

        # redis_pool 存在，正常提供连接
    try:
        async with aioredis.Redis(connection_pool=redis_pool) as redis_client:
            yield redis_client
    except redis.exceptions.RedisError as e:  # 只捕获 Redis 相关的错误
        user_activity_logger.error(f"Redis连接错误: {e}", exc_info=True)
        raise CacheServiceUnavailableError("无法从 Redis 池获取连接。")