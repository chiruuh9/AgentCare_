from pydantic import BaseModel
from typing import Optional

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str
    user_id: int
    patient_id: Optional[int] = None
    full_name: str
    disclaimer: str = "AgentCare does not diagnose Type-2 Diabetes or prescribe treatment. It assists clinicians and patients only."

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    full_name: str
    patient_id: Optional[int] = None

    class Config:
        from_attributes = True
