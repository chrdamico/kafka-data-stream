import click
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from entities.message_producer import ImageSize
from conf.settings import settings
from entities.kafka import KafkaProducerConfig, KafkaConsumerConfig
from entities.minio import MinioConnectionInformation
from repositories.image_storage import ImageStorageRepository
from repositories.kafka_consumer import KafkaConsumer
from repositories.kafka_producer import KafkaProducer
from services.message_consumer import MessageConsumerService
from services.message_producer import MessageProducerService
from utils.logger import init_logger, global_logger


@click.group()
def cli():
    pass


def setup():
    init_logger(settings.LOG_LEVEL)


@click.command(name="produce")
def produce():
    setup()
    message_producer_service = MessageProducerService(
        kafka_producer=KafkaProducer(KafkaProducerConfig(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)),
        data_topic=settings.KAFKA_DATA_TOPIC,
        customer_id=settings.PRODUCER_CUSTOMER_ID,
        image_size=ImageSize(
            width=settings.IMAGE_SIZE_WIDTH, height=settings.IMAGE_SIZE_HEIGHT, channels=settings.IMAGE_SIZE_CHANNELS
        ),
    )
    background_tasks = BlockingScheduler()
    background_tasks.add_job(message_producer_service.produce, CronTrigger(second="*"))
    try:
        global_logger.info("Starting message production")
        background_tasks.start()
    except KeyboardInterrupt:
        background_tasks.shutdown()


@click.command(name="consume")
def consume():
    setup()
    message_consumer_service = MessageConsumerService(
        kafka_consumer=KafkaConsumer(
            KafkaConsumerConfig(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                group_id=settings.KAFKA_GROUP_ID,
                auto_offset_reset=settings.KAFKA_AUTO_OFFSET_RESET,
                topic=settings.KAFKA_DATA_TOPIC,
            )
        ),
        image_storage_repository=ImageStorageRepository(
            database_connection_string=settings.DATABASE_CONNECTION_STRING,
            minio_connection_information=MinioConnectionInformation(
                connection_string=settings.MINIO_CONNECTION_STRING,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                bucket_name=settings.MINIO_BUCKET_NAME,
            ),
        ),
    )

    background_tasks = BlockingScheduler()
    background_tasks.add_job(message_consumer_service.consume, CronTrigger(second="*"))
    try:
        global_logger.info("Starting consuming messages")
        background_tasks.start()
    except KeyboardInterrupt:
        background_tasks.shutdown()


cli.add_command(produce)
cli.add_command(consume)


if __name__ == "__main__":
    cli()
