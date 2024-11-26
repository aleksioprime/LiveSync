from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text

from src.db.postgres import get_db_session
from src.db.redis import get_redis

router = APIRouter()


@router.get("/", status_code=200)
async def ping():
    """
    Эндпоинт для проверки работы web-сервера
    """
    return {"status": "ok", "message": "Server is up and running."}


@router.get("/postgres", status_code=HTTPStatus.OK)
async def postgres_health_check(db_session: AsyncSession = Depends(get_db_session)):
    """
    Эндпоинт для проверки состояния PostgreSQL.
    """
    try:
        result = await db_session.execute(text("SELECT 1"))
        if result.scalar() == 1:
            return {"status": "ok", "message": "Postgres is operational"}
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail={"status": "error", "message": f"Postgres check failed: {str(e)}"},
        )

@router.get("/redis", status_code=HTTPStatus.OK)
async def redis_health_check(redis: Redis = Depends(get_redis)):
    """
    Эндпоинт для проверки состояния Redis.
    """
    try:
        if await redis.ping():
            return {"status": "ok", "message": "Redis is operational"}
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail={"status": "error", "message": f"Redis check failed: {str(e)}"},
        )