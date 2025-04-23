# app/crud/todo.py
from sqlalchemy.ext.asyncio import AsyncSession  # 비동기 세션 지원
from sqlalchemy import select  # SELECT 쿼리 지원
from sqlalchemy.future import select  # SQLAlchemy 2.x 호환성
from uuid import UUID  # UUID 타입 지원
from datetime import datetime, timezone  # 날짜 및 시간 관련 모듈
from typing import Optional, List  # 선택적 값 및 리스트 지원

from app.todo.models import Todo, TodoStatus  # 할 일(Todo) 모델 및 상태 Enum
from app.todo.schemas import (
    TodoCreate,
    TodoUpdate,
)  # Pydantic 스키마 (입력 및 업데이트용)


# ✅ 특정 ID의 Todo 가져오기
async def get_todo(db: AsyncSession, todo_id: UUID) -> Optional[Todo]:
    """
    주어진 todo_id에 해당하는 할 일(Todo)을 데이터베이스에서 조회합니다.

    :param db: 데이터베이스 세션
    :param todo_id: 조회할 할 일의 ID
    :return: Todo 객체 또는 None (존재하지 않는 경우)
    """
    result = await db.execute(select(Todo).where(Todo.id == todo_id))
    return result.scalars().one_or_none()  # 존재하지 않으면 None 반환


# ✅ 모든 Todo 가져오기 (필요시 상태별 필터링 가능)
async def get_todos(
    db: AsyncSession, status: Optional[TodoStatus] = None  # 특정 상태 필터링 (선택적)
) -> List[Todo]:
    """
    모든 할 일(Todo) 목록을 가져오거나, 특정 상태에 따라 필터링하여 조회합니다.

    :param db: 데이터베이스 세션
    :param status: 필터링할 상태 (선택적)
    :return: Todo 객체 리스트
    """
    query = select(Todo)  # 기본적으로 모든 Todo를 조회

    if status:
        query = query.where(Todo.status == status)  # 특정 상태만 필터링

    result = await db.execute(query)
    return result.scalars().all()  # 리스트 반환


# ✅ 새로운 Todo 생성
async def create_todo(db: AsyncSession, todo: TodoCreate) -> Todo:
    """
    새로운 할 일(Todo)을 데이터베이스에 생성합니다.

    :param db: 데이터베이스 세션
    :param todo: 생성할 할 일의 데이터 (Pydantic 스키마)
    :return: 생성된 Todo 객체
    """
    db_todo = Todo(
        title=todo.title,
        content=todo.content,
        status=todo.status,
        start_date=todo.start_date,
        end_date=todo.end_date,
    )
    db.add(db_todo)  # 데이터베이스에 추가
    await db.commit()  # 트랜잭션 커밋
    await db.refresh(db_todo)  # 최신 상태로 갱신
    return db_todo  # 생성된 Todo 반환


# ✅ 기존 Todo 업데이트
async def update_todo(
    db: AsyncSession, todo_id: UUID, todo_update: TodoUpdate
) -> Optional[Todo]:
    """
    주어진 ID의 할 일(Todo)을 업데이트합니다.

    :param db: 데이터베이스 세션
    :param todo_id: 업데이트할 Todo의 ID
    :param todo_update: 업데이트할 데이터 (Pydantic 스키마)
    :return: 업데이트된 Todo 객체 또는 None (존재하지 않는 경우)
    """
    db_todo = await get_todo(db, todo_id)  # 기존 데이터 조회
    if not db_todo:
        return None  # 존재하지 않으면 None 반환

    # Pydantic 스키마에서 변경된 필드만 가져오기
    update_data = todo_update.model_dump(exclude_unset=True)

    # ✅ 업데이트 시간 자동 설정
    update_data["updated_at"] = datetime.now(timezone.utc).replace(tzinfo=None)

    # 필드 업데이트
    for key, value in update_data.items():
        setattr(db_todo, key, value)

    await db.commit()  # 트랜잭션 커밋
    await db.refresh(db_todo)  # 최신 상태로 갱신
    return db_todo  # 업데이트된 Todo 반환


# ✅ Todo 삭제
async def delete_todo(db: AsyncSession, todo_id: UUID) -> bool:
    """
    주어진 ID의 할 일(Todo)을 삭제합니다.

    :param db: 데이터베이스 세션
    :param todo_id: 삭제할 Todo의 ID
    :return: 삭제 성공 여부 (True: 성공, False: 존재하지 않음)
    """
    db_todo = await get_todo(db, todo_id)  # 기존 데이터 조회
    if not db_todo:
        return False  # 존재하지 않으면 False 반환

    await db.delete(db_todo)  # 삭제 실행
    await db.commit()  # 트랜잭션 커밋
    return True  # 삭제 성공
