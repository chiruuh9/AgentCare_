from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class MedicationSchema(BaseModel):
    id: int
    patient_id: int
    name: str
    dosage: str
    frequency: str
    start_date: datetime
    end_date: Optional[datetime] = None
    prescribing_doctor: str

    class Config:
        from_attributes = True

class PrescriptionInterpretationResponse(BaseModel):
    medications: List[MedicationSchema]
    explanation: str
    disclaimer: str = "AgentCare does not diagnose Type-2 Diabetes or prescribe treatment. It assists clinicians and patients only."
