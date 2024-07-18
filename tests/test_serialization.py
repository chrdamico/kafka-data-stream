import numpy

from entities.kafka import ImageDataMessage
from services.message_consumer import MessageConsumerService
from services.message_producer import MessageProducerService


def test_serialization(
    test_message_producer_service: MessageProducerService,
    example_image_data: ImageDataMessage,
    test_message_consumer_service: MessageConsumerService,
):
    serialized_message = test_message_producer_service._serialize_message(example_image_data)
    deserialized_message = test_message_consumer_service._deserialize_message(serialized_message)

    assert deserialized_message.uuid == example_image_data.uuid
    assert deserialized_message.customer_id == example_image_data.customer_id
    assert deserialized_message.sent_at == example_image_data.sent_at
    assert numpy.array_equal(deserialized_message.image_data, example_image_data.image_data)
