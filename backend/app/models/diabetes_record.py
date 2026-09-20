"""
DiabetesRecord model for AgentCare Type-2 Diabetes Decision Support System.

DISCLAIMER: AgentCare does NOT diagnose conditions or prescribe medications.
This record model stores historical readings and unstructured notes to assist clinicians and patients.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class DiabetesRecord(Base):
    """
    Stores longitudinal clinical readings and notes for Type-2 Diabetes management.
    Record types include: hba1c, blood_glucose, history, medication, lifestyle.
    """
    __tablename__ = "diabetes_records"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    record_type = Column(String, nullable=False, index=True)  # 'hba1c', 'blood_glucose', 'history', 'medication', 'lifestyle'
    value = Column(Float, nullable=True)  # e.g., 7.5 for HbA1c, 135 for glucose
    unit = Column(String, nullable=True)   # e.g., '%', 'mg/dL', 'mmol/L'
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    notes = Column(Text, nullable=True)    # Structured clinician/patient notes
    raw_text = Column(Text, nullable=True) # Unstructured transcript or clinical doc text

    # Relationship
    patient_profile = relationship("PatientProfile", back_populates="diabetes_records")

    def __repr__(self):
        return (
            f"<DiabetesRecord(id={self.id}, patient_id={self.patient_id}, "
            f"type='{self.record_type}', value={self.value} {self.unit})>"
        )
