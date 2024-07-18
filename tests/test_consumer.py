from unittest.mock import MagicMock, patch

from services.message_consumer import MessageConsumerService


@patch("repositories.image_storage.ImageStorageRepository.save_image")
def test_simple_consume(
    image_storage_repository: MagicMock,
    example_encoded_batch_image_data: list[bytes],
    test_message_consumer_service: MessageConsumerService,
):
    test_message_consumer_service._get_new_messages = MagicMock(return_value=example_encoded_batch_image_data)

    # Call the consume method
    test_message_consumer_service.consume()

    assert len(image_storage_repository.call_args_list) == len(example_encoded_batch_image_data)


@patch("repositories.image_storage.ImageStorageRepository.save_image")
def test_simple_consume_no_new_data(
    image_storage_repository: MagicMock,
    test_message_consumer_service: MessageConsumerService,
):
    test_message_consumer_service._get_new_messages = MagicMock(return_value=[])

    # Call the consume method
    test_message_consumer_service.consume()
    assert len(image_storage_repository.call_args_list) == 0
