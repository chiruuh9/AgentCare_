from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class RecordUploadRequest(BaseModel):
    raw_text: str

class DiabetesRecordSchema(BaseModel):
    id: int
    patient_id: int
    record_type: str
    value: Optional[float] = None
    unit: Optional[str] = None
    date: datetime
    notes: Optional[str] = None
    raw_text: Optional[str] = None

    class Config:
        from_attributes = True

class DiabetesRecordListResponse(BaseModel):
    records: List[DiabetesRecordSchema]
    disclaimer: str = "AgentCare does not diagnose Type-2 Diabetes or prescribe treatment. It assists clinicians and patients only."
