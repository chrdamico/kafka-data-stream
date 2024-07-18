from confluent_kafka import Consumer, cimpl

from entities.kafka import KafkaConsumerConfig


class KafkaConsumer:
    BATCH_SIZE = 5
    TIMEOUT_SECONDS = 0.1

    def __init__(self, config: KafkaConsumerConfig):
        self._consumer = Consumer(
            {
                "bootstrap.servers": config.bootstrap_servers,
                "group.id": config.group_id,
                "auto.offset.reset": "earliest",
            }
        )
        self._consumer.subscribe(topics=[config.topic])

    def consume(self) -> list[cimpl.Message] | None:
        return self._consumer.consume(num_messages=self.BATCH_SIZE, timeout=self.TIMEOUT_SECONDS)
