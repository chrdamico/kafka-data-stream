import zlib
from datetime import datetime
import uuid
from io import BytesIO

import msgpack
import numpy as np
from PIL import Image

from entities.message_producer import ImageSize
from entities.kafka import ImageDataMessage
from repositories.kafka_producer import KafkaProducer
from utils.logger import global_logger


class MessageProducerService:
    MIN_PIXEL_VALUE = 0
    MAX_PIXEL_VALUE = 256

    BATCH_SIZE = 3

    IMAGE_FORMAT = "PNG"

    def __init__(
        self,
        kafka_producer: KafkaProducer,
        data_topic: str,
        customer_id: int,
        image_size: ImageSize,
    ) -> None:
        self._producer = kafka_producer
        self._data_topic = data_topic
        self.customer_id = customer_id
        self.image_size = image_size

    def produce(self) -> None:
        """Generates a batch of random images and publishes them to a Kafka topic."""
        global_logger.info("Generating a new batch of messages")
        mock_images = [self._generate_image() for _ in range(self.BATCH_SIZE)]
        for item in mock_images:
            self._producer.produce(
                topic=self._data_topic,
                data=self._serialize_message(
                    ImageDataMessage(
                        uuid=uuid.uuid4(),
                        customer_id=self.customer_id,
                        image_data=item,
                        sent_at=datetime.utcnow().isoformat(),
                    )
                ),
            )
        global_logger.info(f"Successfully produced {len(mock_images)} new messages")

    def _generate_image(self) -> bytes:
        """
        Generates a random image by getting a random numpy ndarray and converting it to PIL.Image bytes

        :return: bytes of a random PIL.Image image
        """
        image_array = np.random.randint(
            self.MIN_PIXEL_VALUE,
            self.MAX_PIXEL_VALUE,
            size=(
                self.image_size.height,
                self.image_size.width,
                self.image_size.channels,
            ),
            dtype=np.uint8,
        )
        image = Image.fromarray(image_array)
        img_buffer = BytesIO()
        image.save(img_buffer, format=self.IMAGE_FORMAT)
        return img_buffer.getvalue()

    @staticmethod
    def _serialize_message(message: ImageDataMessage) -> bytes:
        """Serializes and converts to
        :param message: Message to be serialized
        :return: Compressed and serialized message
        """
        msg_dict = {
            "uuid": message.uuid.bytes,
            "customer_id": message.customer_id,
            "sent_at": message.sent_at.timestamp(),
            "image_data": message.image_data,
        }
        packed = msgpack.packb(msg_dict)
        return zlib.compress(packed)
