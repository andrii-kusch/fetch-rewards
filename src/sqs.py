import logging
from boto3 import client
from time import sleep
from botocore.exceptions import ClientError, EndpointConnectionError
from urllib3.exceptions import NewConnectionError

def get_client(endpoint, region):
    return client("sqs", region_name=region, endpoint_url=endpoint)
    
def get_messages_sqs(client, queue_url, wait, max_messages=10, retries=5, delay=5):
    # Attempt to receive messages from sqs. Several attempts will be made with a set delay
    while retries:
        try:  
            response = client.receive_message(QueueUrl=queue_url,
                                              MaxNumberOfMessages=max_messages,
                                              WaitTimeSeconds=wait)
            if not "Messages" in response:
                logging.info("The queue appears to be empty.")
                return
            messages = response["Messages"]
            for message in messages:
                client.delete_message(QueueUrl=queue_url,
                                      ReceiptHandle=message["ReceiptHandle"])
            # generate batches of messages
            yield messages
        except (ClientError, EndpointConnectionError) as error:  #NewConnectionError?
            logging.error(f"Receiveing messages failed. Is sqs ready? Retrying in {delay}, {retries} retries left.")
            logging.debug(f"Following error occurred: {error}")
            retries -= 1
            sleep(delay)
