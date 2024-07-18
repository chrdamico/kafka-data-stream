# Simple Kafka data stream 

This project is a simple kafka-based data streaming application. It defines a producer that generates some random image data 
and a consumer that stores it for long term use. The actual images are stored in [Minio](https://min.io/]). 
An indexing table with metadata about the images is created in [Postgres](https://www.postgresql.org/)

## How to run

### Required containers
Running the application requires having a connection to:
- A Kafka broker
- A postgreSQL instance
- A Minio instance

`docker-compose` files that raise local versions of these are available in the [.local](.local) folder. 
Together with them there is a [`docker-compose.yml`](.local%2Fkafka_ui%2Fdocker-compose.yml) file that raises an 
instance of [KafkaUI](https://docs.kafka-ui.provectus.io/). This is not needed to run the project but is useful for 
debugging and developing.

With the configuration in these `docker-compose` files, web interfaces are available at:
- KafkaUI: http://localhost:8081/
- Minio: http://localhost:9001/

There was not enough time to setup a proper migration solution (for example using [alembic](https://alembic.sqlalchemy.org/en/latest/)).
Therefore tables need to be created manually by connecting to the postgres instance and running the queries in [table_creation](table_creation) 
after connecting to the database with any client. A helper script ([table_creation_helper.py](table_creation%2Ftable_creation_helper.py)) 
that can create the database and the table is provided. This can be run using the same environment as described below.

The project comes with a [pyproject.toml](pyproject.toml). To run the python part, just install the required python 
version (for example using [pyenv](https://github.com/pyenv/pyenv)), then create a `venv` and install the required
dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install .
```

For development purposes and to run tests, it's also possible to install development dependencies
```bash
pip install .[dev]
```

At startup, the application loads settings from the environment. An `.env` file in the [conf](src%2Fconf) folder can be
used to conveniently provide them. A [.env](src%2Fconf%2F.env) file compatible with the configs of the local instances
of all services has been committed with the repo already. Of course, no real secrets should ever be committed this way.
As documentation, a `.env` file should look like 

```
KAFKA_BOOTSTRAP_SERVERS="host:port"
KAFKA_GROUP_ID="my_consumer_group"
KAFKA_AUTO_OFFSET_RESET="beginning"
KAFKA_DATA_TOPIC="kafka_topic"
PRODUCER_CUSTOMER_ID=1234

DATABASE_CONNECTION_STRING="postgresql+psycopg://user:password@host:port/database_name"

MINIO_BUCKET_NAME="bucket_name"
MINIO_CONNECTION_STRING="host:port"
MINIO_ACCESS_KEY="user"
MINIO_SECRET_KEY="password"
```

Entrypoint of the application is a CLI in [manage.py](src%2Fmanage.py). Two commands start the `consumer`
and `producer` respectively. These can be run with `manage produce` and `manage consume`.

## Structure of the project

The folder structure is as follows:
- The entrypoints in `manage.py` are just scheduled calls to the service layer in `services`.
- [services](src%2Fservices): contains most of the actual logic of the application. 
- [repositories](src%2Frepositories): contains all code that communicates with the outside world. 
  - Here are defined simple wrappers to Kafka consumers([kafka_consumer.py](src%2Frepositories%2Fkafka_consumer.py)) and producers ([kafka_producer.py](src%2Frepositories%2Fkafka_producer.py)), as these are often reused within a project with similar configuration
  - [image_storage.py](src%2Frepositories%2Fimage_storage.py) handles the logic of saving and retrieving images.
- [entities](src%2Fentities) contains definitions of any dataclasses (here [Pydantic](https://docs.pydantic.dev/latest/) `BaseModel`s) used in the rest of the code.
- [conf](src%2Fconf) contains the basic settings class. 
- [utils](src%2Futils) just contains a simple logging util.

## Room for improvement
There are many things in this project that would require more work to improve. Here is a non-exhaustive list:

- Initial setup should be done properly in code. 
  - Table creation (and future migrations) should not be manual, but handled by a proper migration tool like `alembic`. 
  - Topic creation should not be implicitly assumed of the producer, but done in a setup stage. Currently if the consumer is started before the producer, the consumer just fails as no topic is there.
- Schemas of messages should ideally not be implicit in code. Kafka has a [schema registry](https://docs.confluent.io/platform/current/schema-registry/index.html) that handles schema contracts between consumers and producers. In this project the consumer and producer are more coupled than necessary by relying both on a unique never changing schema. A proper schema registry makes schema changes easier in case of a migration.
- Exception handling is not comprehensive enough. The project would benefit a lot from better explicit handling of exceptions and logging of them. For example the `KafkaConsumer` just raises an exception if it starts and the topic has not been created.
- Tests should be better structured. Currently, tests run on the same database table and minio bucket as normal runs of the code. 
  - There should be a framework of mocking the external services or at least cleaning them before and after tests
  - A real world application should 100% have a check before tests are started to verify that they are being run on a test database
