import logging
import math
from enum import Enum
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis as AsyncRedis
from pydantic import BaseModel, Field

from app.core.logging_crud import LoggingFastCRUD
from app.core.responses import StandardResponse, Success, PaginationMeta
from app.exceptions.exceptions import ResourceNotFoundException, MissingFieldException, AppException
from app.exceptions.error_codes import ErrorCode
from app.models import Users
from app.schemas import UserCreate, UserUpdate, UserRead, UserResponse
from app.db.session import get_db
from app.db.cache import get_redis

logger = logging.getLogger(__name__)

router = APIRouter()
crud_instance = LoggingFastCRUD(Users)

CACHE_TTL_SECONDS = 300


class UserAction(str, Enum):
    GET_BY_ID = "get_by_id"
    GET_ALL = "get_all"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"

class ActionRequest(BaseModel):
    action: UserAction
    payload: dict = Field(default_factory=dict)


async def _get_by_id_handler(payload: dict, db: AsyncSession, redis: AsyncRedis):
    entity_id = payload.get("id")
    if not entity_id:
        raise MissingFieldException(name="id")

    cache_key = crud_instance._get_cache_key(entity_id)
    try:
        if cached_data := await redis.get(cache_key):
            logger.debug(f"CACHE: Hit for key {cache_key}")
            return UserRead.model_validate_json(cached_data)
    except Exception as e:
        logger.error(f"CACHE_ERROR: Read failed for key {cache_key}: {e}", exc_info=True)

    logger.debug(f"CACHE: Miss for key {cache_key}. Fetching from DB.")
    db_entity = await crud_instance.get(db=db, id=entity_id)
    if not db_entity:
        raise ResourceNotFoundException(detail=f"ID为 {entity_id} 的user未找到。")

    entity_to_cache = UserRead.model_validate(db_entity)
    try:
        await redis.setex(cache_key, CACHE_TTL_SECONDS, entity_to_cache.model_dump_json())
    except Exception as e:
        logger.error(f"CACHE_ERROR: Write failed for key {cache_key}: {e}", exc_info=True)
    return entity_to_cache


async def _get_all_handler(payload: dict, db: AsyncSession, redis: AsyncRedis):
    offset = payload.get("offset", 0)
    limit = payload.get("limit", 100)

    multi_response = await crud_instance.get_multi(db=db, offset=offset, limit=limit)
    # (关键修复) 2. 通过键来正确地获取数据和总数
    orm_list = multi_response['data']
    total_count = multi_response['total_count']
    # items_orm_list, total_count = await item_crud.get_multi(db=db, offset=offset, limit=limit)

    # orm_list, total_count = await crud_instance.get_multi(db=db, offset=offset, limit=limit)
    pydantic_list = [UserRead.model_validate(item) for item in orm_list]
    total_pages = math.ceil(total_count / limit) if limit > 0 else 0
    current_page = (offset // limit) + 1 if limit > 0 else 1
    pagination_meta = {"pagination": PaginationMeta(total_items=total_count, total_pages=total_pages, current_page=current_page, page_size=limit).model_dump()}
    return {"data": UserResponse(data=pydantic_list, total_count=total_count), "meta": pagination_meta}


async def _create_handler(payload: dict, db: AsyncSession, redis: AsyncRedis):
    try:
        create_schema = UserCreate.model_validate(payload)
    except Exception as e:
        raise AppException(ErrorCode.VALIDATION_ERROR, detail=str(e))
    new_orm_instance = await crud_instance.create(db=db, object=create_schema)
    return UserRead.model_validate(new_orm_instance)


async def _update_handler(payload: dict, db: AsyncSession, redis: AsyncRedis):
    entity_id = payload.get("id")
    update_data = payload.get("update_data")
    if not entity_id: raise MissingFieldException(name="id")
    if not update_data: raise MissingFieldException(name="update_data")

    try:
        update_schema = UserUpdate.model_validate(update_data)
    except Exception as e:
        raise AppException(ErrorCode.VALIDATION_ERROR, detail=str(e))
    updated_orm_instance = await crud_instance.update(db=db, object=update_schema, id=entity_id)
    cache_key = crud_instance._get_cache_key(entity_id)
    try:
        await redis.delete(cache_key)
        logger.info(f"CACHE_INVALIDATE: Deleted cache for key {cache_key}")
    except Exception as e:
        logger.error(f"CACHE_ERROR: Failed to DELETE cache key {cache_key}: {e}", exc_info=True)
    return UserRead.model_validate(updated_orm_instance)


async def _delete_handler(payload: dict, db: AsyncSession, redis: AsyncRedis):
    entity_id = payload.get("id")
    if not entity_id:
        raise MissingFieldException(name="id")
    to_delete = await crud_instance.get(db=db, id=entity_id)
    if not to_delete:
        raise ResourceNotFoundException(detail=f"ID为 {entity_id} 的user未找到，无法删除。")
    await crud_instance.delete(db=db, id=entity_id)
    cache_key = crud_instance._get_cache_key(entity_id)
    try:
        await redis.delete(cache_key)
        logger.info(f"CACHE_INVALIDATE: Deleted cache for key {cache_key}")
    except Exception as e:
        logger.error(f"CACHE_ERROR: Failed to DELETE cache key {cache_key}: {e}", exc_info=True)
    return {"message": f"Successfully deleted user with id {entity_id}"}


ACTION_HANDLERS = {
    UserAction.GET_BY_ID: _get_by_id_handler,
    UserAction.GET_ALL: _get_all_handler,
    UserAction.CREATE: _create_handler,
    UserAction.UPDATE: _update_handler,
    UserAction.DELETE: _delete_handler,
}

@router.post("/actions", response_model=StandardResponse, summary="统一处理user操作")
async def handle_user_actions(
        request: ActionRequest,
        db: AsyncSession = Depends(get_db),
        redis: AsyncRedis = Depends(get_redis)
):
    handler = ACTION_HANDLERS.get(request.action)
    if not handler:
        raise AppException(ErrorCode.BAD_REQUEST, detail=f"不支持的操作: '{request.action}'")

    try:
        result = await handler(payload=request.payload, db=db, redis=redis)
        if request.action == UserAction.GET_ALL:
            return Success(data=result.get("data"), meta=result.get("meta"))
        return Success(data=result)
    except Exception as e:
        if isinstance(e, AppException):
            raise e
        logger.error(f"在操作 '{request.action}' 中发生未处理的服务器错误: {e}", exc_info=True)
        raise AppException(ErrorCode.UNEXPECTED_ERROR) from e
