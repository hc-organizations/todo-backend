# app/db/session.py

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import async_session_maker  # DB 세션 팩토리 가져오기


# ✅ 비동기 DB 세션을 제공하는 FastAPI의 Dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI의 Dependency Injection 방식으로 비동기 DB 세션을 제공합니다.
    요청이 끝나면 자동으로 세션을 정리합니다.
    """
    async with async_session_maker() as session:  # 세션 생성
        try:
            yield session  # 세션을 요청하는 엔드포인트에 전달
            await session.commit()  # 정상 실행 시 트랜잭션 커밋
        except Exception:
            await session.rollback()  # 예외 발생 시 롤백
            raise
        finally:
            await session.close()  # 세션 종료
