from datetime import date
from hashlib import sha256
import logging
from time import sleep
    
def mask(value, salt=''):
    # Hashing a string with optional salt
    return sha256((value+salt).encode()).hexdigest()
    
def transform(message):
    # Groom the message before commiting to Postgres
    try:
        message['app_version'] = int(message["app_version"].replace(".", ""))
        message['create_date'] = date.today().strftime("%Y-%m-%d")
        message['ip'] = mask(message['ip'], salt=message['user_id'])
        message['device_id'] = mask(message['device_id'], salt=message['user_id'])
        sleep(0.5)  # Simulated hard work, comment/uncomment to explore replication or run full speed
        return message
    # If anything goes wromng, log and ignore
    except KeyError as error:
        logging.warning(f'Unexpected message format. Following message is ignored: {message}')
        logging.debug(f"Following error occurred: {error}")
    
