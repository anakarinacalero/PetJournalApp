from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

class Reminder(BaseModel):
    id: UUID
    pet_id: UUID
    title: str
    reminder_type: str
    scheduled_at: datetime
    email_sent: bool