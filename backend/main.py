"""
AgentCare FastAPI Main Application.

Multi-Agent AI Clinical Decision Support System for Type-2 Diabetes Management.

DISCLAIMER: AgentCare does NOT diagnose Type-2 Diabetes or prescribe treatment.
It assists clinicians and patients only.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.audit_logging import AuditLoggingMiddleware
from app.api.auth import router as auth_router
from app.api.patients import router as patients_router
from app.api.reminders import router as reminders_router

SAFETY_DISCLAIMER = "AgentCare does not diagnose Type-2 Diabetes or prescribe treatment. It assists clinicians and patients only."

app = FastAPI(
    title="AgentCare API",
    description="Multi-agent AI clinical decision support system for Type-2 Diabetes management.",
    version="0.1.0",
)

# Add Audit Logging Middleware
app.add_middleware(AuditLoggingMiddleware)

# Set up CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers under /api
app.include_router(auth_router, prefix="/api")
app.include_router(patients_router, prefix="/api")
app.include_router(reminders_router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "Welcome to AgentCare API",
        "docs": "/docs",
        "status": "online",
        "disclaimer": SAFETY_DISCLAIMER,
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": "AgentCare Backend",
        "disclaimer": SAFETY_DISCLAIMER,
    }
