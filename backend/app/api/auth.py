"""
Authentication API Router for AgentCare.

DISCLAIMER: AgentCare does not diagnose Type-2 Diabetes or prescribe treatment.
It assists clinicians and patients only.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.security import verify_password, create_access_token
from app.schemas.auth import LoginRequest, Token, UserResponse
from app.models.user import User, PatientProfile
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

SAFETY_DISCLAIMER = "AgentCare does not diagnose Type-2 Diabetes or prescribe treatment. It assists clinicians and patients only."


@router.post("/login", response_model=Token)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticates username/password and issues signed JWT Bearer Token.
    """
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    # Retrieve patient_id if user is a patient
    patient_id = None
    if user.patient_profile:
        patient_id = user.patient_profile.id

    access_token = create_access_token(subject=user.username, role=user.role)
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        role=user.role,
        username=user.username,
        user_id=user.id,
        patient_id=patient_id,
        full_name=user.full_name,
        disclaimer=SAFETY_DISCLAIMER,
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Returns current authenticated user profile.
    """
    patient_id = current_user.patient_profile.id if current_user.patient_profile else None
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        role=current_user.role,
        full_name=current_user.full_name,
        patient_id=patient_id,
    )
