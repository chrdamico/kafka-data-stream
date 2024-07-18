from datetime import datetime
from io import BytesIO
from uuid import UUID

from PIL import Image
from minio import Minio
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from entities.image_metadata import ImageMetadata
from entities.kafka import ImageDataMessage
from entities.minio import MinioConnectionInformation


class ImageStorageRepository:
    IMAGE_SAVE_FORMAT = "PNG"
    MINIO_CONTENT_TYPE = "image/png"

    def __init__(
        self,
        database_connection_string: str,
        minio_connection_information: MinioConnectionInformation,
    ):
        self.engine = create_engine(database_connection_string)
        self.session = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.minio_client = Minio(
            minio_connection_information.connection_string,
            access_key=minio_connection_information.access_key,
            secret_key=minio_connection_information.secret_key,
            secure=False,
        )

        self.minio_bucket_name = minio_connection_information.bucket_name
        self._setup()

    def _setup(self) -> None:
        """Create minio bucket if it does not exist."""
        found = self.minio_client.bucket_exists(self.minio_bucket_name)
        if not found:
            self.minio_client.make_bucket(self.minio_bucket_name)

    def get_image_by_uuid(self, image_uuid: UUID) -> Image:
        """
        Gets an image from the store by uuid
        :param image_uuid: uuid of the image to get
        :return: Image
        """
        image_metadata = self.get_image_metadata(image_uuid=image_uuid)
        image_address = self._get_image_address(message=image_metadata)
        response = self.minio_client.get_object(bucket_name=self.minio_bucket_name, object_name=image_address)
        return Image.open(BytesIO(response.read()))

    def get_image_metadata(self, image_uuid: UUID) -> ImageMetadata:
        """
        Gets metadata of the image from the store by uuid
        :param image_uuid: uuid of the image to get
        :return: metadata of the image
        """
        with self.session() as session:
            query = text("""SELECT * FROM image_storage WHERE uuid = :uuid""")
            result = session.execute(query, {"uuid": str(image_uuid)})
        return ImageMetadata.model_validate(result.fetchone(), from_attributes=True)

    def save_image(self, message: ImageDataMessage) -> None:
        """
        Save an incoming image to permanent storage.
        Takes care of db transactions to make sure that no partial saving is possible
        :param message: message containing image data to be saved
        """
        try:
            with self.session() as session:
                with session.begin():
                    self._save_image_data(message=message)
                    self._save_image_metadata(session, message=message)
        except Exception as e:
            print(f"An error occurred: {e}")
            raise

    def _save_image_metadata(self, session: Session, message: ImageDataMessage) -> None:
        """
        Saves image metadata to the store
        :param session: session to use for db operation
        :param message: message containing image data
        """
        query = text("""
            INSERT INTO image_storage (uuid, customer_id, image_address, sent_at, received_at)
            VALUES (:uuid, :customer_id, :image_address, :sent_at, :received_at)
        """)
        session.execute(
            query,
            {
                "uuid": message.uuid,
                "customer_id": message.customer_id,
                "image_address": self._get_image_address(message=message),
                "sent_at": message.sent_at,
                "received_at": datetime.now().isoformat(),
            },
        )

    def _save_image_data(self, message: ImageDataMessage) -> None:
        """
        Saves image data to the store
        :param message: message containing image data
        """
        # Get a buffer over the object that we want to save
        buffer = BytesIO(message.image_data)

        self.minio_client.put_object(
            bucket_name=self.minio_bucket_name,
            object_name=self._get_image_address(message=message),
            data=buffer,
            length=buffer.getbuffer().nbytes,
            content_type=self.MINIO_CONTENT_TYPE,
        )

    @staticmethod
    def _get_image_address(message: ImageDataMessage | ImageMetadata) -> str:
        return f"{message.customer_id}/{message.uuid}"
