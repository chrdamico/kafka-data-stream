import zlib
from datetime import datetime
import uuid

import msgpack

from entities.kafka import ImageDataMessage
from repositories.image_storage import ImageStorageRepository
from repositories.kafka_consumer import KafkaConsumer
from utils.logger import global_logger


class MessageConsumerService:
    def __init__(
        self,
        kafka_consumer: KafkaConsumer,
        image_storage_repository: ImageStorageRepository,
    ):
        self._consumer = kafka_consumer
        self.image_storage_repository = image_storage_repository

    def consume(self) -> None:
        """Consumes messages and stores images to permanent storage"""
        global_logger.info("Consuming...")
        messages = self._get_new_messages()
        for message in messages:
            self.image_storage_repository.save_image(message)
        global_logger.info(f"Successfully consumed {len(messages)} new messages")

    def _get_new_messages(self) -> list[ImageDataMessage]:
        """Queries Kafka to get new messages.

        :return: list of Image data messages
        """
        messages = self._consumer.consume()
        return [self._deserialize_message(message_bytes=message.value()) for message in messages]

    @staticmethod
    def _deserialize_message(message_bytes: bytes) -> ImageDataMessage:
        """
        Deserializes and decompresses an incoming message into actual data
        :param message_bytes: Raw incoming message as bytes
        :return: Image data message
        """
        decompressed = zlib.decompress(message_bytes)
        msg_dict = msgpack.unpackb(decompressed)
        return ImageDataMessage(
            uuid=uuid.UUID(bytes=msg_dict["uuid"]),
            customer_id=msg_dict["customer_id"],
            sent_at=datetime.fromtimestamp(msg_dict["sent_at"]),
            image_data=msg_dict["image_data"],
        )
