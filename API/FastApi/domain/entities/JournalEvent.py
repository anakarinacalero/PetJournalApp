from datetime import datetime
from uuid import UUID
class JournalEvent:
    id: UUID
    pet_id: UUID
    event_type: str
    description: str
    created_at: datetime