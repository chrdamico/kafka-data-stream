from unittest.mock import patch

from services.message_producer import MessageProducerService


@patch("repositories.kafka_producer.KafkaProducer.produce")
def test_simple_produce(
    produce_function_mock,
    test_message_producer_service: MessageProducerService,
):
    # Check that kafka produce is called BATCH_SIZE times every time we generate_messages()
    test_message_producer_service.produce()
    assert len(produce_function_mock.call_args_list) == test_message_producer_service.BATCH_SIZE
