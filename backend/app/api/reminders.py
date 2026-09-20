"""
Reminders API Router for AgentCare.

DISCLAIMER: AgentCare does not diagnose Type-2 Diabetes or prescribe treatment.
It assists clinicians and patients only.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.reminder import Reminder
from app.models.user import User
from app.api.deps import get_current_user, verify_patient_access
from app.schemas.reminder import ReminderSchema

router = APIRouter(prefix="/reminders", tags=["Reminders"])

SAFETY_DISCLAIMER = "AgentCare does not diagnose Type-2 Diabetes or prescribe treatment. It assists clinicians and patients only."


@router.patch("/{id}/complete", response_model=ReminderSchema)
def mark_reminder_complete(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Marks a scheduled reminder as completed.
    """
    reminder = db.query(Reminder).filter(Reminder.id == id).first()
    if not reminder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")

    # Verify patient ownership / access
    verify_patient_access(reminder.patient_id, current_user, db)

    reminder.is_completed = True
    db.commit()
    db.refresh(reminder)
    
    return reminder
