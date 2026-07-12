from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

class AIConsultation(BaseModel):
    id: UUID
    pet_id: UUID
    question: str
    answer: str
    risk_level: str
    created_at: datetime