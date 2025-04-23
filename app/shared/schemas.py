# app/schemas/base.py
from pydantic import BaseModel, ConfigDict  # Pydantic 기본 모델 및 설정
from app.shared.utils import to_camel_case  # snake_case → camelCase 변환 함수


# ✅ 모든 Pydantic 스키마에서 camelCase 변환을 적용하는 기본 모델
class CamelBaseModel(BaseModel):
    """모든 스키마의 기본 클래스로, camelCase 변환을 적용합니다."""

    model_config = ConfigDict(
        from_attributes=True,  # SQLAlchemy ORM 객체를 Pydantic 모델로 변환 가능하게 설정
        populate_by_name=True,  # 필드 이름을 alias로 변환 가능하게 설정
        alias_generator=to_camel_case,  # snake_case를 camelCase로 변환하는 함수 적용
    )
