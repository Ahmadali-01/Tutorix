from fastapi import APIRouter

from app.api.v1 import auth, courses, questions, assignments, rag, analytics, agents

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
api_router.include_router(questions.router, prefix="/questions", tags=["questions"])
api_router.include_router(assignments.router, prefix="/assignments", tags=["assignments"])
api_router.include_router(rag.router, prefix="/rag", tags=["rag"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])