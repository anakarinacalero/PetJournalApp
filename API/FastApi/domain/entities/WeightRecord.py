from datetime import datetime
from uuid import UUID


class WeightRecord:
    id: UUID
    pet_id: UUID
    weight: float
    recorded_at: datetime