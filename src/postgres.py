import logging
from time import sleep
from psycopg2 import connect, OperationalError
from psycopg2.extras import execute_batch

query = "INSERT INTO user_logins VALUES (%(user_id)s, %(device_type)s, %(ip)s, %(device_id)s, %(locale)s, %(app_version)s, %(create_date)s)"

def get_connection_and_cursor(retries=5, delay=5):
    # Attempt to establish a connection to Postgres. Several attempts will be made with a set delay
    while retries:
        try:
            connection = connect(user="postgres",
                                password="postgres",
                                host="postgres",  # local debug: "localhost" <-> "postgres"
                                port="5432",
                                database="postgres")
            cursor = connection.cursor()
            return connection, cursor
        except OperationalError as error:
            logging.error(f"Connection to Postgres failed. Is Postgres ready? Retrying in {delay}, {retries} retries left.")
            logging.debug(f"Following error occurred: {error}")
            retries -= 1
            sleep(delay)
    return None, None

def flush_buffer(connection, cursor, buffer):
    # Committing messages to Postgress
    try:
        execute_batch(cursor, query, buffer)
        connection.commit()
        return len(buffer)
    except KeyError as error:
        logging.error("Unable to commit buffered records to Postgres.")
        logging.debug(f"Following error occurred: {error}")

