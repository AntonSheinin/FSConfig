# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=maybe-no-member
# pylint: disable=line-too-long

import logging
from typing import Callable
import requests
from requests.auth import HTTPBasicAuth
import redis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

redis_client = redis.Redis(host='redis', port=6379, db=0)

def api_call(query: str,
             request_method: str,
             json_payload: dict,
             username: str,
             password: str) -> dict:

    url = 'http://193.176.179.222:8085/flussonic/api/v3/'

    if request_method == 'GET':
        resp = requests.get(''.join((url, query)), auth = HTTPBasicAuth(username, password))
        logger.info('Status code : %s', resp.status_code)

    elif request_method == 'PUT':
        resp = requests.put(''.join((url, query)), json = json_payload, auth = HTTPBasicAuth(username, password))
        logger.info('Status code : %s', resp.status_code)

    else:
        print('request method not supported')

    return resp.json()


def config_load_update(func: Callable) -> Callable:
    def wrapper(session: str) -> list:

        uploaded_config = {}

        uploaded_config.update(redis_client.json().get('uploaded_config' + session, '.'))
        choosen_channels = redis_client.lrange('choosen_channels' + session, 0, -1)
        choosen_channels = [channel.decode('utf-8') for channel in choosen_channels]

        output = func(uploaded_config, choosen_channels, session)

        redis_client.json().set('uploaded_config' + session, '.', output[1])
        return output[0]

    return wrapper


def changed_channels_list_update(session: str, channel_name: str, channel_entity: str) -> None:

    changed_channels = []

    if redis_client.exists('changed_channels' + session):
        changed_channels = redis_client.json().get('changed_channels' + session, '.')
        
    changed_channels.append({'name' : channel_name, 'entity' : channel_entity})

    redis_client.json().set('changed_channels' + session, '.', changed_channels)
