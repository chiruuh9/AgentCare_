"""
Medication model for AgentCare Type-2 Diabetes Decision Support System.

DISCLAIMER: AgentCare does NOT prescribe medications or alter prescriptions.
It aids in interpreting existing prescriptions and organizing dosage schedules for Type-2 Diabetes.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class Medication(Base):
    """
    Stores patient medication regimens for Type-2 Diabetes management (e.g., Metformin, Insulin).
    """
    __tablename__ = "medications"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)               # e.g., "Metformin"
    dosage = Column(String, nullable=False)             # e.g., "500mg"
    frequency = Column(String, nullable=False)          # e.g., "twice daily with meals"
    start_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_date = Column(DateTime, nullable=True)          # None if ongoing
    prescribing_doctor = Column(String, nullable=False) # e.g., "Dr. Sarah Jenkins"

    # Relationship
    patient_profile = relationship("PatientProfile", back_populates="medications")

    def __repr__(self):
        return f"<Medication(id={self.id}, name='{self.name}', dosage='{self.dosage}', frequency='{self.frequency}')>"
