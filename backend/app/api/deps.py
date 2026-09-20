"""
FastAPI Dependencies for Security, JWT Auth, DB Session, and Role-Based Access Control (RBAC).

DISCLAIMER: AgentCare does not diagnose Type-2 Diabetes or prescribe treatment.
It assists clinicians and patients only.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.security import decode_access_token
from app.models.user import User, PatientProfile

security_scheme = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Extracts and validates JWT Bearer token from Request header."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token payload",
        )
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User associated with token not found",
        )
    
    return user


def verify_patient_access(patient_id: int, current_user: User, db: Session):
    """
    Role-Based Access Control Rule:
    - Clinicians can access any patient profile.
    - Patients can ONLY access their own patient profile.
    """
    if current_user.role == "clinician":
        return True
    
    # Check if current patient user owns this profile
    profile = db.query(PatientProfile).filter(PatientProfile.user_id == current_user.id).first()
    if not profile or profile.id != patient_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Patients may only access their own records.",
        )
    return True
