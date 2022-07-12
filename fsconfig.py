#fsconfig.py - Webapp for Flussonic Streaming Server mutliple streams config edit

import json
import requests
from requests.auth import HTTPBasicAuth
import secrets
from random import random
from urllib import response
import redis
from redis.commands.json.path import Path
from bottle import route, run, template, request, static_file, error, default_app, response

allowed_IP = ['127.0.0.1', '62.90.52.94', '94.130.136.116']
menu_links = {'main-menu' : 'MainMenu',
             'choose-channels' : 'ChooseChannels',
             'dvr-settings' : 'DVRSettings',
             'source-priority' : 'SourcePriority',
             'stream-sorting' : 'StreamSorting',
             'config-upload-json' : 'ConfigUploadJson',
             'config-download-json' : 'ConfigDownloadJson',
             'config-upload-api' : 'ConfigUploadApi',
             'config-download-api' : 'ConfigDownloadApi'}

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def api_call(query, request_method, json_payload, username, password):

    url = 'http://193.176.179.222:8085/flussonic/api/v3/'

    if request_method == 'GET':
        response = requests.get(''.join((url, query)), auth = HTTPBasicAuth(username, password))

    elif request_method == 'PUT':  
        response = requests.put(''.join((url, query)), json = json_payload, auth = HTTPBasicAuth(username, password))
        print(response.status_code)

    else:
        print('request method not supported')

    return response.json()

def ConfigLoadUpdate(func):
    def Wrapper(session):

        uploaded_config = {}

        uploaded_config.update(redis_client.json().get('uploaded_config' + session, Path.root_path()))
        choosen_channels = redis_client.lrange('choosen_channels' + session, 0, -1)
        choosen_channels = [channel.decode('utf-8') for channel in choosen_channels]

        output = func(uploaded_config, choosen_channels)

        redis_client.json().set('uploaded_config' + session, Path.root_path(), output[1])
        return output[0]

    return Wrapper

@route('/<url>', method=['GET','POST'])
def Router(url):

    if (request.environ.get('HTTP_X_FORWARDED_FOR') is not None and request.environ.get('HTTP_X_FORWARDED_FOR') not in allowed_IP) or request.environ.get('REMOTE_ADDR') not in allowed_IP:
        print(request.environ.get('REMOTE_ADDR'))
        return(HTTPErrorHandling(403))

    session_id = request.get_cookie('sessionid')
    print(session_id)
    if session_id is None:
        session_id = secrets.token_urlsafe(8)
        response.set_cookie('sessionid', session_id)

    if url in menu_links:
        return(globals()[menu_links[url]](session_id))

    return(HTTPErrorHandling(404))

@route('/')
def RouterWrapper():
        return Router('main-menu')

def HTTPErrorHandling(code):

    if code == 403:
        return('access denied')
    if code == 404:
        return('page doesnt exist')

def MainMenu(session):
    return template('templates/main_menu.tpl')

def ChooseChannels(session):

    channel_list = []
    choosen_channels = []

    for stream in redis_client.json().get('uploaded_config' + session, Path('.streams')):
            channel_list.append(stream['name'])

    if request.method == 'GET':
        redis_client.ltrim('choosen_channels' + session, 1, 0)
        return template('templates/choose_channels_form.tpl', names = channel_list)

    for channel in channel_list:
        if request.forms.get(channel) == 'on':
            redis_client.rpush('choosen_channels' + session, channel)
            choosen_channels.append(channel)
            
    return template('templates/choosen_channels.tpl', names = choosen_channels)

@ConfigLoadUpdate
def DVRSettings(config, choosen_channels):

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

    return template('templates/dvr_complete.tpl'), config

@ConfigLoadUpdate
def SourcePriority(config, choosen_channels):

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

    return template('templates/source_priority_complete.tpl'), config

@ConfigLoadUpdate
def StreamSorting(config, choosen_channels):

    if request.method == 'GET':
        return template('templates/stream_sorting_channels_form.tpl', names = choosen_channels), config

    for stream in config['streams']:
        if stream['name'] in choosen_channels and request.forms.get(stream['name']) != '':
            stream['position'] = request.forms.get(stream['name'])

    config['streams'].sort(key=lambda x: int(x.get('position')))

    return template('templates/sorting_complete.tpl'), config

def ConfigUploadApi(session):

    if request.method == 'GET':
        return template('templates/auth_form_upload.tpl')

    config = {}

    username = request.forms.get('username')
    password = request.forms.get('password')

    config = redis_client.json().get('uploaded_config' + session, Path('.streams'))
    print(config)
    choosen_channels = redis_client.lrange('choosen_channels' + session, 0, -1)
    choosen_channels = [channel.decode('utf-8') for channel in choosen_channels]

    for channel in choosen_channels:
        response = api_call(''.join(('streams/', channel)), 'PUT', config['streams'][channel], username, password)
        print(response.status_code)

def ConfigDownloadApi(session):

    if request.method == 'GET':
        return template('templates/auth_form_download.tpl')

    username = request.forms.get('username')
    password = request.forms.get('password')

    stream_call = api_call('streams?limit=1','GET', {}, username, password)

    config = api_call(''.join(('streams?limit=', str(stream_call['estimated_count'] + 10))),'GET', {}, username, password)

    redis_client.json().set('uploaded_config' + session, Path.root_path(), config)

    return template('templates/upload_complete.tpl')

def ConfigUploadJson(session):

    if request.method == 'GET':
        return template('templates/upload_file_form.tpl')

    redis_client.json().set('uploaded_config' + session, Path.root_path(), json.load(request.files.get('config').file))

    return template('templates/upload_complete.tpl')

def ConfigDownloadJson(session):

    with open('./output_config.json', 'w') as file:
        json.dump(redis_client.json().get('uploaded_config' + session, Path.root_path()), file)

    return static_file('output_config.json', root='./', download=True)

#def main():
#   run(server='gunicorn', host='10.100.102.6', port=8080)
    #run(host='127.0.0.1', port=8080)

app = default_app()

#if __name__ == '__main__':
#    main()
