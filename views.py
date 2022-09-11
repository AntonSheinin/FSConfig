# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=maybe-no-member
# pylint: disable=line-too-long

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


@config_load_update
def dvr_settings(config: dict, choosen_channels: list, session: str):

    if request.method == 'GET':
        return template('templates/dvr_settings_form.tpl'), config

    disc_space_limit_gb = int(request.forms.get('space_limit_gb')) * 1024 ** 3
    disc_space_limit_perc = int(request.forms.get('space_limit_perc'))
    dvr_limit = int(request.forms.get('duration'))
    dvr_root = request.forms.get('path')

    for stream in config['streams']:
        if stream['name'] in choosen_channels:
            stream['dvr'] = {"disk_space" : disc_space_limit_gb,
                             "disk_limit" : disc_space_limit_perc,
                             "disk_usage_limit" : disc_space_limit_perc,
                             "dvr_limit" : dvr_limit,
                             "expiration" : dvr_limit,
                             "root" : dvr_root,
                             "storage_limit" : disc_space_limit_gb}
            if dvr_limit == 0:
                del stream['dvr']

            changed_channels_list_update(session, stream['name'], 'dvr')

    return template('templates/dvr_complete.tpl'), config


@config_load_update
def source_priority(config: dict, choosen_channels: list, session: str):

    if request.method == 'GET':
        return template('templates/source_priority_form.tpl'), config

    first_condition = request.forms.get('first_condition')
    first_condition_priority = request.forms.get('first_condition_priority')
    second_condition = request.forms.get('second_condition')
    second_condition_priority = request.forms.get('second_condition_priority')
    default_priority = request.forms.get('default_priority')

    for stream in config['streams']:
        if stream['name'] in choosen_channels:
            for url in stream['inputs']:
                if first_condition in url['url'] and first_condition != '':
                    url['priority'] = first_condition_priority
                elif second_condition in url['url'] and second_condition != '':
                    url['priority'] = second_condition_priority
                else:
                    url['priority'] = default_priority

            changed_channels_list_update(session, stream['name'], 'inputs')

    return template('templates/source_priority_complete.tpl'), config


@config_load_update
def stream_sorting(config: dict, choosen_channels: list, session: str):

    if request.method == 'GET':
        return template('templates/stream_sorting_channels_form.tpl', names = choosen_channels), config

    for stream in config['streams']:
        if stream['name'] in choosen_channels and request.forms.get(stream['name']) != '':
            stream['position'] = request.forms.get(stream['name'])
            changed_channels_list_update(session, stream['name'], 'position')

    config['streams'].sort(key=lambda x: int(x.get('position')))

    return template('templates/sorting_complete.tpl'), config


def config_upload_to_server_api(session: str):

    if request.method == 'GET':
        return template('templates/auth_form_upload.tpl')

    username = request.forms.get('username')
    password = request.forms.get('password')

    uploaded_config = redis_client.json().get('uploaded_config' + session, '.')
    changed_channels = redis_client.json().get('changed_channels' + session, '.')

    for channel in changed_channels['changed_channels']:
        name = channel['name']
        entity = channel['entity']
    
    #changed_channels['changed_channels'] = [api_call(stream) in uploaded_config['streams'] if stream['name'] in changed_channels['changed_channels']]

    #for stream in uploaded_config['streams']:
    #    if stream['name'] in changed_channels['changed_channels']:
    #        logger.info(json.loads('{' + changed_channels['changed_channels']['entity'] + ':' + stream[changed_channels['entity']] + '}'))
    #        break
    #        #api_call(''.join(('streams/', stream['name'])), 'PUT', json.loads('{' + changed_channels['entity'] + ':' + stream[changed_channels['entity']] + '}'), username, password)
    #    logger.info('changes in %s not found', stream['name'])

    #redis_client.delete('changed_channels' + session)

    return template('templates/upload_api_complete.tpl')


def config_load_from_server_api(session: str):

    if request.method == 'GET':
        return template('templates/auth_form_download.tpl')

    username = request.forms.get('username')
    password = request.forms.get('password')

    stream_call = api_call('streams?limit=1','GET', {}, username, password)

    config = api_call(''.join(('streams?limit=', str(stream_call['estimated_count'] + 10))),'GET', {}, username, password)

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