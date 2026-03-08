"""
FastAPI Application Entry Point
Main application setup and configuration
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import settings
from src.routes.course import router as course_router
from src.routes.explanation import router as explanation_router
from src.services.ai_service import AIServiceError

app = FastAPI(title="Explaino API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(explanation_router)
app.include_router(course_router)


@app.get("/api/health")
async def health_check() -> dict:
    return {"status": "ok"}


@app.exception_handler(AIServiceError)
async def ai_service_error_handler(request: Request, exc: AIServiceError) -> JSONResponse:
    return JSONResponse(
        status_code=502,
        content={"detail": str(exc)},
    )
