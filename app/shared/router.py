from fastapi import APIRouter
from app.todo.endpoints import router as todo_router

router = APIRouter()


router.include_router(todo_router, prefix="/todos", tags=["todos"])
