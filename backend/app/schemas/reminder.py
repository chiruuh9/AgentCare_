from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ReminderSchema(BaseModel):
    id: int
    patient_id: int
    reminder_type: str
    message: str
    scheduled_time: datetime
    is_completed: bool

    class Config:
        from_attributes = True

class ReminderListResponse(BaseModel):
    reminders: List[ReminderSchema]
    disclaimer: str = "AgentCare does not diagnose Type-2 Diabetes or prescribe treatment. It assists clinicians and patients only."
