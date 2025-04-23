# app/schemas/todo.py
from app.shared.schemas import CamelBaseModel  # 기본 Pydantic 스키마 (camelCase 지원)
from uuid import UUID  # UUID 타입 지원
from datetime import datetime  # 날짜 타입 지원
from enum import Enum  # Enum 타입 지원
from typing import Optional  # 선택적 필드 지원
from pydantic import model_validator  # Pydantic의 데이터 검증 기능 추가


# ✅ 할 일(Todo) 상태를 정의하는 Enum (SQLAlchemy 모델과 일치)
class TodoStatus(str, Enum):
    """할 일(Todo)의 상태를 나타내는 Enum"""

    NOT_STARTED = "NOT_STARTED"
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


# ✅ 기본 Todo 스키마 (공통 속성)
class TodoBase(CamelBaseModel):
    """할 일(Todo)의 기본 속성 (공통 속성)"""

    title: str  # 제목
    content: str  # 내용


# ✅ Todo 생성 시 사용할 스키마
class TodoCreate(TodoBase):
    """할 일(Todo) 생성 요청 시 사용되는 스키마"""

    status: TodoStatus = TodoStatus.NOT_STARTED  # 기본 상태는 NOT_STARTED
    start_date: Optional[datetime] = None  # 선택적 시작일
    end_date: Optional[datetime] = None  # 선택적 종료일

    # ✅ 시작일과 종료일 검증 로직 추가
    @model_validator(mode="after")
    def validate_dates(self) -> "TodoCreate":
        """종료일이 시작일보다 이전이면 오류 발생"""
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("종료 날짜는 시작 날짜 이후여야 합니다")
        return self


# ✅ Todo 업데이트 시 사용할 스키마
class TodoUpdate(CamelBaseModel):
    """할 일(Todo) 업데이트 요청 시 사용되는 스키마 (모든 필드 선택적)"""

    title: Optional[str] = None  # 제목 (선택적)
    content: Optional[str] = None  # 내용 (선택적)
    status: Optional[TodoStatus] = None  # 상태 (선택적)
    start_date: Optional[datetime] = None  # 시작일 (선택적)
    end_date: Optional[datetime] = None  # 종료일 (선택적)

    # ✅ 최소 하나 이상의 필드가 있어야 업데이트 가능
    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "TodoUpdate":
        """업데이트 시 최소한 하나 이상의 필드가 제공되어야 함"""
        values = {k: v for k, v in self.__dict__.items() if v is not None}
        if not values:
            raise ValueError("최소한 하나 이상의 필드가 제공되어야 합니다")
        return self


# ✅ 데이터베이스에서 가져온 Todo 정보를 반환할 스키마
class Todo(CamelBaseModel):
    """데이터베이스에서 가져온 Todo 정보를 반환할 스키마"""

    id: UUID  # UUID 기본키
    title: str  # 제목
    content: str  # 내용
    status: TodoStatus  # 상태
    start_date: Optional[datetime] = None  # 시작일
    end_date: Optional[datetime] = None  # 종료일
    created_at: datetime  # 생성일
    updated_at: datetime  # 수정일
