# app/models/todo.py
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)  # SQLAlchemy ORM의 타입 어노테이션을 지원하는 모듈
from sqlalchemy import String, Enum, DateTime  # SQL 타입 지정
from sqlalchemy.dialects.postgresql import (
    UUID as PgUUID,
)  # PostgreSQL에서 UUID 타입 사용
from datetime import datetime, timezone  # 날짜 및 시간 관련 모듈
from uuid import uuid4  # UUID 생성 함수
from app.shared.models import Base  # 기본 Base 모델 가져오기
from typing import Optional  # 선택적(Nullable) 필드 지원
from enum import Enum as PyEnum  # Enum 클래스 (상태 필드에서 사용)


# ✅ 할 일(Todo) 상태를 관리하는 Enum 클래스
class TodoStatus(str, PyEnum):
    """할 일(Todo)의 상태를 나타내는 Enum"""

    NOT_STARTED = "NOT_STARTED"
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


# ✅ 할 일(Todo) 모델 정의
class Todo(Base):
    """할 일(Todo) 모델 - PostgreSQL의 todo 테이블에 매핑"""

    __tablename__ = "todo"  # 테이블 이름 설정

    # ✅ UUID 기본키 (PostgreSQL의 UUID 타입 사용)
    id: Mapped[PgUUID] = mapped_column(PgUUID, primary_key=True, default=uuid4)

    # ✅ 제목과 내용 필드 (최대 길이 255)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(String(255))

    # ✅ 상태 필드 (Enum 타입 사용, 기본값: NOT_STARTED)
    status: Mapped[TodoStatus] = mapped_column(
        Enum(TodoStatus), default=TodoStatus.NOT_STARTED
    )

    # ✅ 시작일 및 종료일 (Nullable 허용)
    start_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    end_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ✅ 생성 시간 (기본값: UTC 현재 시간)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc).replace(
            tzinfo=None
        ),  # UTC 시간으로 설정
    )

    # ✅ 수정 시간 (기본값: UTC 현재 시간, 업데이트 시 자동 변경)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        onupdate=lambda: datetime.now(timezone.utc).replace(
            tzinfo=None
        ),  # 업데이트 시 현재 시간으로 변경
    )
