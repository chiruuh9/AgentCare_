"""
Reminder model for AgentCare Type-2 Diabetes Decision Support System.

DISCLAIMER: AgentCare does NOT diagnose or prescribe.
Reminders assist patients with Type-2 Diabetes self-management schedules (glucose checks, medication timing, lifestyle).
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class Reminder(Base):
    """
    Stores scheduled patient reminders for Type-2 Diabetes adherence and monitoring.
    Types: 'medication', 'glucose_check', 'appointment', 'lifestyle'.
    """
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    reminder_type = Column(String, nullable=False, index=True) # 'medication', 'glucose_check', 'appointment', 'lifestyle'
    message = Column(Text, nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)

    # Relationship
    patient_profile = relationship("PatientProfile", back_populates="reminders")

    def __repr__(self):
        return (
            f"<Reminder(id={self.id}, patient_id={self.patient_id}, "
            f"type='{self.reminder_type}', scheduled='{self.scheduled_time}', completed={self.is_completed})>"
        )
