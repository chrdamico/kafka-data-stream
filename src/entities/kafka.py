from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class KafkaConsumerConfig(BaseModel):
    bootstrap_servers: str
    group_id: str
    auto_offset_reset: str
    topic: str


class KafkaProducerConfig(BaseModel):
    bootstrap_servers: str


class ImageDataMessage(BaseModel):
    uuid: UUID
    customer_id: int
    image_data: bytes
    sent_at: datetime
