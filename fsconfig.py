#fsconfig.py - Webapp for Flussonic Streaming Server mutliple streams config edit

import json
import requests
from requests.auth import HTTPBasicAuth
import secrets
from random import random
from urllib import response
import redis
from bottle import route, run, template, request, static_file, error, default_app, response

allowed_IP = ['127.0.0.1', '62.90.52.94', '94.130.136.116', '10.100.102.1']
menu_links = {'main-menu' : 'main_menu',
             'choose-channels' : 'choose_channels',
             'dvr-settings' : 'dvr_settings',
             'source-priority' : 'source_priority',
             'stream-sorting' : 'stream_sorting',
             'config-load-json' : 'load_config_file_json',
             'config-download-json' : 'download_config_file_json',
             'config-upload-api' : 'config_upload_to_server_api',
             'config-load-api' : 'config_load_from_server_api'}

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def api_call(query, request_method, json_payload, username, password):

    url = 'http://193.176.179.222:8085/flussonic/api/v3/'

    if request_method == 'GET':
        response = requests.get(''.join((url, query)), auth = HTTPBasicAuth(username, password))
        print(response.status_code)

    elif request_method == 'PUT':  
        response = requests.put(''.join((url, query)), json = json_payload, auth = HTTPBasicAuth(username, password))
        print(response.status_code)

    else:
        print('request method not supported')

    return response.json()

def config_load_update(func):
    def wrapper(session):

        uploaded_config = {}

        uploaded_config.update(redis_client.json().get('uploaded_config' + session, '.'))
        choosen_channels = redis_client.lrange('choosen_channels' + session, 0, -1)
        choosen_channels = [channel.decode('utf-8') for channel in choosen_channels]

        output = func(uploaded_config, choosen_channels, session)

        redis_client.json().set('uploaded_config' + session, '.', output[1])
        return output[0]

    return wrapper

@route('/<url>', method=['GET','POST'])
def router(url):

    if (request.environ.get('HTTP_X_FORWARDED_FOR') is not None and request.environ.get('HTTP_X_FORWARDED_FOR') not in allowed_IP) or request.environ.get('REMOTE_ADDR') not in allowed_IP:
        print(request.environ.get('REMOTE_ADDR'))
        return(http_error_handling(403))

    session_id = request.get_cookie('sessionid')
    print(session_id)
    if session_id is None:
        session_id = secrets.token_urlsafe(8)
        response.set_cookie('sessionid', session_id)

    if url in menu_links:
        return(globals()[menu_links[url]](session_id))

    return(http_error_handling(404))

@route('/')
def router_wrapper():
        return router('main-menu')

def http_error_handling(code):

    if code == 403:
        return('access denied')
    if code == 404:
        return('page doesnt exist')

def main_menu(session):
    return template('templates/main_menu.tpl')

def changed_channels_list_update(session, channel_name, channel_entity):

    changed_channels = {}

    if not redis_client.exists('changed_channels' + session):
        redis_client.json().set('changed_channels' + session,'.', {'count' : '0', 'streams' : []})

    count = int(redis_client.json().get('changed_channels' + session, '.count'))
    changed_channels = redis_client.json().get('changed_channels'+ session, '.')

    changed_channels['streams'].update({'name' : channel_name, 'entity' : channel_entity})
    count += 1
    changed_channels.update({'count' : count})

    redis_client.json().set('changed_channels' + session, '.', changed_channels)
    
    #redis_client.json().set('changed_channels' + session, '.streams.[]', {'name' : channel_name, 'entity' : channel_entity})
    #redis_client.set('changed_channels_count' + session, str(count + 1))

def choose_channels(session):

    channel_list = []
    choosen_channels = []

    for stream in redis_client.json().get('uploaded_config' + session, '.streams'):
            channel_list.append(stream['name'])

    if request.method == 'GET':
        redis_client.ltrim('choosen_channels' + session, 1, 0)
        return template('templates/choose_channels_form.tpl', names = channel_list)

    for channel in channel_list:
        if request.forms.get(channel) == 'on':
            choosen_channels.append(channel)

    redis_client.rpush('choosen_channels' + session, *choosen_channels)
    
    return template('templates/choosen_channels.tpl', names = choosen_channels)

@config_load_update
def dvr_settings(config, choosen_channels, session):

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
def source_priority(config, choosen_channels, session):

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
        
            changed_channels_list_update(session, stream['name'], 'source_priority')

    return template('templates/source_priority_complete.tpl'), config

@config_load_update
def stream_sorting(config, choosen_channels, session):

    if request.method == 'GET':
        return template('templates/stream_sorting_channels_form.tpl', names = choosen_channels), config

    for stream in config['streams']:
        if stream['name'] in choosen_channels and request.forms.get(stream['name']) != '':
            stream['position'] = request.forms.get(stream['name'])

            changed_channels_list_update(session, stream['name'], 'position')

    config['streams'].sort(key=lambda x: int(x.get('position')))

    return template('templates/sorting_complete.tpl'), config

def config_upload_to_server_api(session):

    if request.method == 'GET':
        return template('templates/auth_form_upload.tpl')

    username = request.forms.get('username')
    password = request.forms.get('password')

    changed_channels = redis_client.json().get('changed_channels' + session,'.')
    uploaded_config = redis_client.json().get('uploaded_config' + session, '.')
    
    print(changed_channels)

    for i in changed_channels:
        print(i['name'])

    for stream in uploaded_config['streams']:
        if stream['name'] in changed_channels:
            print(stream['name'])
            api_call(''.join(('streams/', stream['name'])), 'PUT', stream[changed_channels['entity']], username, password)

    #redis_client.json().delete('changed_channels' + session)
    #redis_client.delete('changed_channels_count' + session)


def config_load_from_server_api(session):

    if request.method == 'GET':
        return template('templates/auth_form_download.tpl')

    username = request.forms.get('username')
    password = request.forms.get('password')

    stream_call = api_call('streams?limit=1','GET', {}, username, password)

    config = api_call(''.join(('streams?limit=', str(stream_call['estimated_count'] + 10))),'GET', {}, username, password)

    redis_client.json().set('uploaded_config' + session, '.', config)

    return template('templates/upload_complete.tpl')

def load_config_file_json(session):

    if request.method == 'GET':
        return template('templates/upload_file_form.tpl')

    redis_client.json().set('uploaded_config' + session, '.', json.load(request.files.get('config').file))

    return template('templates/upload_complete.tpl')

def download_config_file_json(session):

    with open('./output_config.json', 'w') as file:
        json.dump(redis_client.json().get('uploaded_config' + session, '.'), file)

    return static_file('output_config.json', root='./', download=True)

#def main():
#   run(server='gunicorn', host='10.100.102.6', port=8080)
    #run(host='127.0.0.1', port=8080)

app = default_app()

#if __name__ == '__main__':
#    main()
