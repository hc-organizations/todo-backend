# migrations/env.py

import asyncio
from logging.config import fileConfig  # Alembic 로깅 설정

from sqlalchemy import pool
from sqlalchemy.engine import engine_from_config  # SQLAlchemy 엔진 생성
from alembic import context  # Alembic의 마이그레이션 실행 컨텍스트

from app.core.config import settings  # 환경 변수에서 DB URL 가져오기
from app.shared.models import Base  # SQLAlchemy의 Base 클래스 (모든 테이블 정보 포함)

# ✅ Alembic 설정 파일 (`alembic.ini`)을 로드하여 로그 설정 적용
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ✅ 마이그레이션 대상 메타데이터 (ORM 모델의 테이블 정보)
target_metadata = Base.metadata


# ✅ 데이터베이스 URL을 반환하는 함수
def get_url():
    return settings.SYNC_DATABASE_URL  # 동기 DB URL 사용 (Alembic은 async 지원 X)


# ✅ 오프라인 마이그레이션 실행 함수 (SQL 파일만 생성)
def run_migrations_offline():
    """
    오프라인 모드에서 마이그레이션을 실행 (DB 연결 없이 SQL 파일 생성)
    alembic upgrade head --sql > migration.sql 명령어 실행 시 사용됨.
    """
    context.configure(
        url=get_url(),  # 데이터베이스 URL 설정
        target_metadata=target_metadata,  # 마이그레이션 대상 테이블 정보 설정
        literal_binds=True,  # SQLAlchemy가 변수 값을 직접 SQL에 바인딩
        dialect_opts={"paramstyle": "named"},  # SQL 바인딩 방식 지정
    )

    # 트랜잭션을 시작하고 마이그레이션 실행
    with context.begin_transaction():
        context.run_migrations()


# ✅ 온라인 마이그레이션 실행 함수 (DB에 직접 적용)
def run_migrations_online():
    """
    온라인 모드에서 마이그레이션을 실행 (데이터베이스에 직접 적용)
    alembic upgrade head 명령어 실행 시 사용됨.
    """
    connectable = engine_from_config(
        config.get_section(
            config.config_ini_section
        ),  # alembic.ini의 설정을 가져와 엔진 생성
        prefix="sqlalchemy.",  # 설정값 앞에 "sqlalchemy."가 붙은 항목만 가져옴
        poolclass=pool.NullPool,  # 연결 풀을 비활성화 (Alembic은 단기 실행이므로 필요 없음)
        url=get_url(),  # 데이터베이스 URL 설정
    )

    # DB 연결을 설정하고 마이그레이션 실행
    with connectable.connect() as connection:
        context.configure(
            connection=connection,  # DB 연결을 설정
            target_metadata=target_metadata,  # 테이블 정보 제공
        )
        with context.begin_transaction():
            context.run_migrations()


# ✅ 실행 모드에 따라 온라인 또는 오프라인 마이그레이션 실행
if context.is_offline_mode():
    run_migrations_offline()  # 오프라인 모드 실행 (SQL 파일 생성)
else:
    run_migrations_online()  # 온라인 모드 실행 (DB에 직접 적용)
