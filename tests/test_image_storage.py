from io import BytesIO

import pytest
import sqlalchemy
from PIL import Image, ImageChops

from entities.kafka import ImageDataMessage
from repositories.image_storage import ImageStorageRepository


def test_save_and_get_image(
    test_image_storage_repository: ImageStorageRepository,
    example_image_data: ImageDataMessage,
):
    # Save an image
    test_image_storage_repository.save_image(message=example_image_data)

    # Retrieve its metadata and check that it's the same
    image_metadata = test_image_storage_repository.get_image_metadata(image_uuid=example_image_data.uuid)

    assert image_metadata.uuid == example_image_data.uuid
    assert image_metadata.customer_id == example_image_data.customer_id

    # Retrieve the image and check that it's the same
    saved_image = test_image_storage_repository.get_image_by_uuid(image_uuid=example_image_data.uuid)
    example_image = Image.open(BytesIO(example_image_data.image_data))

    # Check if the images have the same mode and size
    if example_image.mode != saved_image.mode or example_image.size != example_image.size:
        raise

    # Compute the difference between the images and assert that it's all black
    assert not ImageChops.difference(saved_image, example_image).getbbox()


def test_no_double_saving(
    test_image_storage_repository: ImageStorageRepository,
    example_image_data: ImageDataMessage,
):
    # Save an image
    test_image_storage_repository.save_image(message=example_image_data)

    # Attempting to save the same image multiple times should result in an error
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        test_image_storage_repository.save_image(message=example_image_data)
