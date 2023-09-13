from sys import exit
import json
import os
import logging
from mask import transform
from postgres import get_connection_and_cursor, flush_buffer
from sqs import get_client, get_messages_sqs

# Configuration
endpoint = "http://localstack:4566/"  # local debug: "http://localhost:4566/" <-> "http://localstack:4566"
queue_url = "http://localhost:4566/000000000000/login-queue"
region = os.getenv('AWS_REGION', 'us-east-1')
keep_listening = os.getenv('keep_listening', 'False').lower() in ('true', '1', 't', 'yes', 'y')
long_pooling = os.getenv('long_pooling', 10)
max_messages = os.getenv('max_messages', 10)
writting_buffer_size = os.getenv('max_messages', 20)
logging.basicConfig(level=logging.INFO)

# Resources initialization
sqs_client = get_client(endpoint, region)
connection, cursor = get_connection_and_cursor()
writting_buffer = []
wait_for_messages_secs = 0
records_received, records_processed, records_commited = 0, 0, 0
if not connection:
    logging.error('Unable to initiate postgres connection.')
    exit(1)

# Main
while True:
    # As long as sqs yields batches...
    for read_batch in get_messages_sqs(sqs_client, queue_url, wait_for_messages_secs, max_messages):
        for message in read_batch:
            records_received += 1
            # Extract message...
            data = json.loads(message["Body"])
            if transformed_data := transform(data):
                # Buffer of transformation was successful, ignore otherwise
                writting_buffer.append(transformed_data)
            # Once size of writing buffer reached (or exceeded), commit buffered messages and clear the buffer
            if len(writting_buffer) >= writting_buffer_size:
                records_commited += flush_buffer(connection, cursor, writting_buffer) or 0
                records_processed += len(writting_buffer)
                writting_buffer.clear()
    # Leftover messages
    if writting_buffer:
        records_commited += flush_buffer(connection, cursor, writting_buffer) or 0
        records_processed += len(writting_buffer)
    # If pipeline is set to keep listening to queue, stay and switch to sleep waiting
    if keep_listening:
        logging.info('Requested to keep listening to the queue. Switching to long pooling...')
        wait_for_messages_secs = long_pooling
    # Otherwise, break the loop and be done
    else:
        break

logging.info("Processing complete.")
logging.info(f"Received {records_received} records, {records_processed} processed, {records_commited} commited.")