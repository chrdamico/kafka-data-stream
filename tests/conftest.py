import uuid
from datetime import datetime

import pytest
from minio import Minio

from entities.message_producer import ImageSize
from conf.settings import Settings
from entities.kafka import (
    KafkaConsumerConfig,
    KafkaProducerConfig,
    ImageDataMessage,
)
from entities.minio import MinioConnectionInformation
from repositories.image_storage import ImageStorageRepository
from repositories.kafka_consumer import KafkaConsumer
from repositories.kafka_producer import KafkaProducer
from services.message_consumer import MessageConsumerService
from services.message_producer import MessageProducerService


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    settings = Settings()
    settings.IMAGE_SIZE_WIDTH = 32
    settings.IMAGE_SIZE_HEIGHT = 32
    return settings


@pytest.fixture(scope="session")
def minio_client(test_settings: Settings) -> Minio:
    return Minio(
        test_settings.MINIO_CONNECTION_STRING,
        access_key=test_settings.access_key,
        secret_key=test_settings.secret_key,
        secure=False,
    )


@pytest.fixture(scope="session")
def test_kafka_consumer(test_settings: Settings) -> KafkaConsumer:
    return KafkaConsumer(
        KafkaConsumerConfig(
            bootstrap_servers=test_settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id=test_settings.KAFKA_GROUP_ID,
            auto_offset_reset=test_settings.KAFKA_AUTO_OFFSET_RESET,
            topic=test_settings.KAFKA_DATA_TOPIC,
        )
    )


@pytest.fixture(scope="session")
def test_kafka_producer(test_settings: Settings) -> KafkaProducer:
    return KafkaProducer(
        KafkaProducerConfig(
            bootstrap_servers=test_settings.KAFKA_BOOTSTRAP_SERVERS,
        )
    )


@pytest.fixture(scope="session")
def test_message_producer_service(
    test_kafka_producer: KafkaProducer, test_settings: Settings
) -> MessageProducerService:
    return MessageProducerService(
        kafka_producer=test_kafka_producer,
        data_topic=test_settings.KAFKA_DATA_TOPIC,
        customer_id=test_settings.PRODUCER_CUSTOMER_ID,
        image_size=ImageSize(
            width=test_settings.IMAGE_SIZE_WIDTH,
            height=test_settings.IMAGE_SIZE_HEIGHT,
            channels=test_settings.IMAGE_SIZE_CHANNELS,
        ),
    )


@pytest.fixture(scope="session")
def test_image_storage_repository(test_settings: Settings) -> ImageStorageRepository:
    return ImageStorageRepository(
        database_connection_string=test_settings.DATABASE_CONNECTION_STRING,
        minio_connection_information=MinioConnectionInformation(
            connection_string=test_settings.MINIO_CONNECTION_STRING,
            access_key=test_settings.MINIO_ACCESS_KEY,
            secret_key=test_settings.MINIO_SECRET_KEY,
            bucket_name=test_settings.MINIO_BUCKET_NAME,
        ),
    )


@pytest.fixture(scope="session")
def test_message_consumer_service(
    test_settings: Settings,
    test_kafka_consumer: KafkaConsumer,
    test_image_storage_repository: ImageStorageRepository,
) -> MessageConsumerService:
    return MessageConsumerService(
        kafka_consumer=test_kafka_consumer,
        image_storage_repository=test_image_storage_repository,
    )


@pytest.fixture
def example_image_data_as_bytes(
    test_message_producer_service: MessageProducerService,
) -> bytes:
    return test_message_producer_service._generate_image()


@pytest.fixture()
def example_image_data(example_image_data_as_bytes: bytes) -> ImageDataMessage:
    return ImageDataMessage(
        uuid=uuid.uuid4(),
        customer_id=1,
        image_data=example_image_data_as_bytes,
        sent_at=datetime.utcnow(),
    )


@pytest.fixture()
def example_encoded_batch_image_data(
    example_image_data_as_bytes: bytes,
    test_message_producer_service: MessageProducerService,
) -> list[bytes]:
    batch_image_data = [
        ImageDataMessage(
            uuid=uuid.uuid4(),
            customer_id=1,
            image_data=example_image_data_as_bytes,
            sent_at=datetime.utcnow(),
        )
        for _ in range(5)
    ]
    return [test_message_producer_service._serialize_message(image_data) for image_data in batch_image_data]
