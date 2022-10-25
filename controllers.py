# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=maybe-no-member

import json
import logging
import redis
from bottle import template, request, static_file
from models import config_load_update, changed_channels_list_update, api_call


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

redis_client = redis.Redis(host='redis', port=6379, db=0)


def main_menu(_):
    return template('templates/main_menu.tpl')


def choose_channels(session: str):

    channel_list = [stream['name'] for stream in redis_client.json().get('uploaded_config' + session, '.streams')]
    choosen_channels = []

    if request.method == 'GET':
        redis_client.ltrim('choosen_channels' + session, 1, 0)
        return template('templates/choose_channels_form.tpl', names = channel_list)

    choosen_channels = [channel for channel in channel_list if request.forms.get(channel) == 'on']
    redis_client.rpush('choosen_channels' + session, *choosen_channels)

    return template('templates/choosen_channels.tpl', names = choosen_channels)


def direct_api_query(session: str):

    if request.method == 'GET':
        return template('templates/direct_api_query.tpl')

    choosen_channels = redis_client.lrange('choosen_channels' + session, 0, -1)
    choosen_channels = [channel.decode('utf-8') for channel in choosen_channels]

    username = request.forms.get('username')
    password = request.forms.get('password')
    api_query = request.forms.get('api_query')

    for stream in choosen_channels:
        api_call('streams/' + stream, 'PUT', json.loads(api_query), username, password)

    redis_client.delete('choosen_channels' + session)

    return template('templates/direct_api_query_complete.tpl')


def source_add(session: str):

    if request.method == 'GET':
        return template('templates/source_add.tpl')

    choosen_channels = redis_client.lrange('choosen_channels' + session, 0, -1)
    choosen_channels = [channel.decode('utf-8') for channel in choosen_channels]
    uploaded_config = redis_client.json().get('uploaded_config' + session, '.')

    username = request.forms.get('username')
    password = request.forms.get('password')

    for stream in uploaded_config['streams']:
        if stream['name'] in choosen_channels:
            if not [source for source in stream['inputs'] if 'sby04' in source['url']]:
                for source in stream['inputs']:
                    if 'sby01' in source['url']:
                        new_source = 'tshttp://sby04.gmdostavka.ru:'+source['url'][-5:]
                        query = f'{{"inputs" : [{{"$index" : 10, "url" : "{new_source}", "priority" : 0}}]}}'
                        logger.info(query)
                        api_call('streams/' + stream['name'], 'PUT', json.loads(query), username, password)
                        break

    redis_client.delete('uploaded_config' + session)
    redis_client.delete('choosen_channels' + session)

    return template('templates/source_add_complete.tpl')


@config_load_update
def dvr_settings(config: dict, choosen_channels: list, session: str):

    changed = {}

    if request.method == 'GET':
        return template('templates/dvr_settings_form.tpl'), config

    disc_space_limit_gb = int(request.forms.get('space_limit_gb')) * 1024 ** 3
    disc_space_limit_perc = int(request.forms.get('space_limit_perc'))
    dvr_limit = int(request.forms.get('duration'))
    dvr_root = request.forms.get('path')

    for stream in config['streams']:
        if stream['name'] in choosen_channels:
            changed['dvr'] = {"disk_space" : disc_space_limit_gb,
                              "disk_limit" : disc_space_limit_perc,
                              "disk_usage_limit" : disc_space_limit_perc,
                              "dvr_limit" : dvr_limit,
                              "expiration" : dvr_limit,
                              "root" : dvr_root,
                              "storage_limit" : disc_space_limit_gb}

            if dvr_limit == 0:
                del stream['dvr']

            changed_channels_list_update(session, stream['name'], 'dvr', changed['dvr'])

    return template('templates/dvr_complete.tpl'), config


@config_load_update
def source_priority(config: dict, choosen_channels: list, session: str):

    if request.method == 'GET':
        return template('templates/source_priority_form.tpl'), config

    first_condition = request.forms.get('first_condition')
    second_condition = request.forms.get('second_condition')

    if (first_condition_priority := request.forms.get('first_condition_priority')) == '':
        first_condition_priority = -1
    else:
        first_condition_priority = int(first_condition_priority)

    if (second_condition_priority := request.forms.get('second_condition_priority')) == '':
        second_condition_priority = -1
    else:
        second_condition_priority = int(second_condition_priority)

    if (default_priority := request.forms.get('default_priority')) == '':
        default_priority = -1
    else:
        default_priority = int(default_priority)

    logger.info(choosen_channels)

    for stream in config['streams']:
        if stream['name'] in choosen_channels:
            for url in stream['inputs']:
                if first_condition in url['url'] and first_condition != '' and first_condition_priority > -1:
                    url['priority'] = first_condition_priority
                elif second_condition in url['url'] and second_condition != '' and second_condition_priority > -1:
                    url['priority'] = second_condition_priority
                elif default_priority > -1:
                    url['priority'] = default_priority

            stream['inputs'].sort(key=lambda x: int(x.get('priority')))

            #changed_channels_list_update(session, stream['name'], 'inputs')

    return template('templates/source_priority_complete.tpl'), config


@config_load_update
def stream_sorting(config: dict, choosen_channels: list, session: str):

    if request.method == 'GET':
        return template('templates/stream_sorting_channels_form.tpl', names = choosen_channels), config

    for stream in config['streams']:
        if stream['name'] in choosen_channels and request.forms.get(stream['name']) != '':
            stream['position'] = request.forms.get(stream['name'])
            changed_channels_list_update(session, stream['name'], 'position', request.forms.get(stream['name']))

    config['streams'].sort(key=lambda x: int(x.get('position')))

    return template('templates/sorting_complete.tpl'), config


def config_upload_to_server_api(session: str):

    if request.method == 'GET':
        return template('templates/auth_form_upload.tpl')

    username = request.forms.get('username')
    password = request.forms.get('password')

    uploaded_config = redis_client.json().get('uploaded_config' + session, '.')
    changed_channels = redis_client.json().get('changed_channels' + session, '.')

    for stream in uploaded_config['streams']:
        for _, value in enumerate(changed_channels):
            if stream['name'] == value['name']:
                changed_keys = json.loads(''.join(('{"', value['entity'], '"', ':', json.dumps(value['changes'])+'}')))
                api_call('streams/' + stream['name'], 'PUT', changed_keys, username, password)

    redis_client.delete('changed_channels' + session)
    redis_client.delete('choosen_channels' + session)

    return template('templates/upload_api_complete.tpl')


def config_load_from_server_api(session: str):

    if request.method == 'GET':
        return template('templates/auth_form_download.tpl')

    username = request.forms.get('username')
    password = request.forms.get('password')

    stream_call = api_call('streams?limit=1','GET', {}, username, password)

    config = api_call(''.join(('streams?limit=', str(stream_call['estimated_count']))),'GET', {}, username, password)

    redis_client.json().set('uploaded_config' + session, '.', config)

    return template('templates/upload_complete.tpl')


def load_config_file_json(session: str):

    if request.method == 'GET':
        return template('templates/upload_file_form.tpl')

    redis_client.json().set('uploaded_config' + session, '.', json.load(request.files.get('config').file))

    return template('templates/upload_complete.tpl')


def download_config_file_json(session: str):

    with open('./output_config.json', 'w', encoding='utf-8') as file:
        json.dump(redis_client.json().get('uploaded_config' + session, '.'), file)

    return static_file('output_config.json', root='./', download=True)
