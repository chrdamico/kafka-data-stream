from typing import Any

from confluent_kafka import Producer

from entities.kafka import KafkaProducerConfig


class KafkaProducer:
    MAX_MESSAGE_SIZE_BYTES = 104857600

    def __init__(self, config: KafkaProducerConfig):
        self._producer = Producer(
            {
                "bootstrap.servers": config.bootstrap_servers,
                "message.max.bytes": self.MAX_MESSAGE_SIZE_BYTES,
            }
        )

    def produce(self, topic: str, data: Any) -> None:
        self._producer.produce(topic=topic, value=data)
        self._producer.flush()
