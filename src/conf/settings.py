import os
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

env_file_path = os.path.join(os.path.dirname(__file__), ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_file_path, env_file_encoding="utf-8", extra="ignore")

    LOG_LEVEL: Literal["DEBUG", "INFO", "WARN", "ERROR"] = "INFO"
    """
    The level of logging to be provided.
    """

    KAFKA_BOOTSTRAP_SERVERS: str
    """
    Location of the kafka bootstrap server
    """

    KAFKA_GROUP_ID: str
    """Group ID of the Kafka consumer"""

    KAFKA_AUTO_OFFSET_RESET: Literal["latest", "earliest", "beginning"]
    """Auto offset setting of the Kafka consumer"""

    KAFKA_DATA_TOPIC: str
    """Topic over which data is transferred"""

    DATABASE_CONNECTION_STRING: str
    """Connection string to postgres database"""

    MINIO_BUCKET_NAME: str
    """Bucket name in which to save images"""

    MINIO_CONNECTION_STRING: str
    """Connection string to minio"""

    MINIO_ACCESS_KEY: str
    """Minio access key"""

    MINIO_SECRET_KEY: str
    """Minio secret key"""

    PRODUCER_CUSTOMER_ID: int
    """Customer ID to be written by the consumer"""

    IMAGE_SIZE_WIDTH: int = 1920
    IMAGE_SIZE_HEIGHT: int = 1080
    IMAGE_SIZE_CHANNELS: int = 3
    """Size of the generated image"""


settings: Settings = Settings()
