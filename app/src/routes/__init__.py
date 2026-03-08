"""
API Routes Package
"""

from src.routes.course import router as course_router
from src.routes.explanation import router as explanation_router

__all__ = [
    "course_router",
    "explanation_router",
]
