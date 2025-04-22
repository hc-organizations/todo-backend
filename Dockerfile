############################################
# 1) Builder 스테이지: 패키지 설치 & 빌드
############################################
FROM python:3.12-slim AS builder

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치 (빌드에 필요한 libpq-dev 포함)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
  && rm -rf /var/lib/apt/lists/*

# Poetry 설치 (버전 고정)
RUN pip install --no-cache-dir poetry==2.1.1

# Poetry 설정: 컨테이너 내에서 venv 미생성
RUN poetry config virtualenvs.create false

# 의존성 파일만 복사 후 설치
COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root --no-interaction

# (Optional) 애플리케이션 코드 빌드나 마이그레이션 스크립트 실행 등
# COPY . .
# RUN poetry run alembic upgrade head

############################################
# 2) Runtime 스테이지: 경량 이미지
############################################
FROM python:3.12-slim

WORKDIR /app

# 런타임에 필요한 시스템 의존성만 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
  && rm -rf /var/lib/apt/lists/*

# non-root 사용자 생성
RUN useradd --create-home appuser
USER appuser

# Builder에서 설치된 패키지와 바이너리 복사
COPY --from=builder --chown=appuser:appuser /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder --chown=appuser:appuser /usr/local/bin /usr/local/bin

# 애플리케이션 코드 복사
COPY --chown=appuser:appuser . .

# 환경변수 (필요 시 외부에서 주입)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# 포트 노출
EXPOSE 8000

# 프로덕션용 커맨드: Gunicorn + Uvicorn 워커
CMD ["gunicorn", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--reload", \
     "app.main:app"]
