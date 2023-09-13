import unittest
from moto import mock_sqs
from json import dumps as json_dumps
from boto3 import resource

from src.sqs import get_client, get_messages_sqs

test_data = {"field1": "test1", "field2": "test2", "field3": "test3"}
region = 'us-east-1'
message_number = 20

class TestSQS(unittest.TestCase):
    @mock_sqs
    def test_get_from_queue(self):
        # Creates a mack sqs queue and posts a set number of identical messages to it
        queue = resource('sqs', region_name=region).create_queue(QueueName='Test_queue')
        for _ in range(message_number):
            queue.send_message(MessageBody=json_dumps(test_data))
        # Use implemented methods to receive messages
        client = get_client(queue.url, region)
        response = get_messages_sqs(client, queue.url, wait=0)
        # response should not be empty
        assert response is not None
        # Unpacking response from generator into list
        response = list(response)
        message_ids = set()
        for batch in response:
            for message in batch:
                # Messages, though identical, have different IDs
                assert message['Body'] == json_dumps(test_data)
                message_ids.add(message['MessageId'])
        assert len(message_ids) == message_number