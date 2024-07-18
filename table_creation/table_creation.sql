create database kafka_data_transfer;


CREATE TABLE image_storage (
    uuid UUID PRIMARY KEY, -- Is indexed by default in Postgresql
    customer_id INT,
    image_address TEXT,
    sent_at TIMESTAMP,
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
