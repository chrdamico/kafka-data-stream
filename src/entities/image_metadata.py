from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ImageMetadata(BaseModel):
    uuid: UUID
    customer_id: int
    image_address: str
    sent_at: datetime
    received_at: datetime
