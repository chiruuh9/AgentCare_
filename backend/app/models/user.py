"""
User and PatientProfile models for AgentCare Type-2 Diabetes Decision Support System.

DISCLAIMER: AgentCare is a decision support tool for Type-2 Diabetes management.
It does NOT diagnose medical conditions or prescribe medications.
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class User(Base):
    """
    Represents system users (Clinicians and Patients) accessing AgentCare for Type-2 Diabetes support.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # "clinician" or "patient"
    full_name = Column(String, nullable=False)

    # Relationships
    patient_profile = relationship("PatientProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"


class PatientProfile(Base):
    """
    Represents patient baseline profile data specific to Type-2 Diabetes management.
    Used for context organizing and history summarizing (no auto-diagnosis or prescription).
    """
    __tablename__ = "patient_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)
    diabetes_duration_years = Column(Float, nullable=False)  # Duration living with Type-2 Diabetes
    target_hba1c = Column(Float, nullable=True, default=7.0)  # Clinician-specified target HbA1c (%)

    # Relationships
    user = relationship("User", back_populates="patient_profile")
    diabetes_records = relationship("DiabetesRecord", back_populates="patient_profile", cascade="all, delete-orphan")
    medications = relationship("Medication", back_populates="patient_profile", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="patient_profile", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<PatientProfile(id={self.id}, user_id={self.user_id}, target_hba1c={self.target_hba1c})>"
