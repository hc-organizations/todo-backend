# app/db/base.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from app.core.config import settings  # 환경 변수에서 DB 설정을 불러옴
import logging

logger = logging.getLogger(__name__)

# ✅ 비동기 SQLAlchemy 엔진 생성 (Azure PostgreSQL 연결)
engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,  # 환경 변수에서 DB URL 가져오기
    echo=settings.DB_ECHO_LOG,  # SQL 쿼리 로그 출력 여부
    future=True,  # SQLAlchemy 2.x 스타일 사용
    pool_pre_ping=True,  # 연결 풀에서 비정상 연결을 감지하여 복구
    poolclass=NullPool,  # 연결 풀 비활성화 (Azure에서는 개별 연결 관리가 일반적)
)

# ✅ 비동기 세션 팩토리 생성 (세션 관리를 위한 Factory)
async_session_maker = async_sessionmaker(
    bind=engine,  # 위에서 생성한 엔진을 바인딩
    class_=AsyncSession,  # 비동기 세션 클래스 사용
    expire_on_commit=False,  # 커밋 후 객체 만료 방지 (데이터 유지)
    autocommit=False,  # 자동 커밋 비활성화 (명시적으로 트랜잭션 관리)
    autoflush=False,  # 자동 flush 비활성화 (수동 flush 필요)
)


# ✅ 데이터베이스 초기화 함수 (테이블 생성)
async def init_db():
    """
    데이터베이스가 존재하지 않는 경우 테이블을 자동 생성합니다.
    Azure PostgreSQL에 연결하여 초기화 수행.
    """
    from app.shared.models import Base  # ORM 모델의 메타데이터 가져오기
    from app.todo.models import Todo  # ORM 모델의 메타데이터 가져오기

    try:
        async with engine.begin() as conn:  # 트랜잭션 시작
            await conn.run_sync(
                Base.metadata.create_all
            )  # ORM 모델을 기반으로 테이블 생성
    except Exception as e:
        logger.error(
            f"Database initialization failed: {e}", exc_info=True
        )  # 오류 발생 시 로그 기록
        raise
