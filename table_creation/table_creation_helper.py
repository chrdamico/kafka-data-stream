import psycopg
from urllib.parse import urlparse
from conf.settings import settings
from psycopg.rows import dict_row


def parse_connection_string(conn_str):
    # Parse the SQLAlchemy-style connection string
    parsed = urlparse(conn_str)

    # Extract components
    username = parsed.username
    password = parsed.password
    host = parsed.hostname
    port = parsed.port
    database = parsed.path.lstrip("/")

    # Construct psycopg-compatible connection string
    psycopg_conn_str = f"dbname={database} user={username} password={password} host={host} port={port}"
    return psycopg_conn_str, database


def create_database_and_table(conn_str):
    psycopg_conn_str, original_db = parse_connection_string(conn_str)

    # Connect to the default database (usually 'postgres')
    default_conn_str = psycopg_conn_str.replace(f"dbname={original_db}", "dbname=postgres")
    conn = psycopg.connect(default_conn_str)
    conn.autocommit = True
    cur = conn.cursor(row_factory=dict_row)

    # Create the kafka_data_transfer database
    try:
        cur.execute("CREATE DATABASE kafka_data_transfer;")
        print("Database kafka_data_transfer created successfully.")
    except psycopg.errors.DuplicateDatabase:
        print("Database kafka_data_transfer already exists.")

    # Close the initial connection
    cur.close()
    conn.close()

    # Update the connection string for the new database
    new_conn_str = psycopg_conn_str.replace(f"dbname={original_db}", "dbname=kafka_data_transfer")

    # Reconnect to the new database
    new_conn = psycopg.connect(new_conn_str)
    new_cur = new_conn.cursor(row_factory=dict_row)

    # Create the image_storage table
    create_table_query = """
    CREATE TABLE IF NOT EXISTS image_storage (
        uuid UUID PRIMARY KEY,
        customer_id INT,
        image_address TEXT,
        sent_at TIMESTAMP,
        received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    new_cur.execute(create_table_query)
    new_conn.commit()
    print("Table image_storage created successfully.")

    # Close the connection
    new_cur.close()
    new_conn.close()


if __name__ == "__main__":
    connection_string = settings.DATABASE_CONNECTION_STRING
    create_database_and_table(connection_string)
