import unittest
from unittest import mock
from unittest.mock import ANY
from src.postgres import flush_buffer, get_connection_and_cursor

test_data = [{'test1': 'data1'}, {'test2': 'data2'}]
connection_args = {"user": ANY, "password": ANY,
                   "host": "postgres", "port":"5432", "database":"postgres"}
query = "INSERT INTO user_logins VALUES (%(user_id)s, %(device_type)s, %(ip)s, %(device_id)s, %(locale)s, %(app_version)s, %(create_date)s)"

class TestPosgres(unittest.TestCase):
    @mock.patch("src.postgres.connect")
    @mock.patch("src.postgres.execute_batch")
    def test_connect_and_flush(self, mock_execute_batch, mock_connect):
        # Use implemented method to obtain connection to Postres and a cursor        
        connection, cursor = get_connection_and_cursor()
        # Connection should be called with correct arguments
        mock_connect.assert_called_once_with(**connection_args)
        # Validating connection and cursor
        mock_connection = mock_connect.return_value
        mock_cursor = mock_connection.cursor.return_value
        assert connection == mock_connection
        assert cursor == mock_cursor
        # Use implemented method to flush buffer and commit messages to Postgres  
        flush_buffer(connection, cursor, test_data)
        # Assert that the right query was used...
        mock_execute_batch.assert_called_once_with(cursor, query, test_data)
        # ...and that connection was called to commit
        mock_connection.commit.assert_called()
        
        
