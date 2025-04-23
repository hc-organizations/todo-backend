# app/models/base.py
from sqlalchemy.orm import DeclarativeBase
import pytz
from sqlalchemy import MetaData

kst = pytz.timezone("Asia/Seoul")


# ✅ SQLAlchemy의 기본 Base 클래스를 정의하는 파일
class Base(DeclarativeBase):
    """모든 모델이 상속받는 기본 Base 클래스"""

    metadata = MetaData()
