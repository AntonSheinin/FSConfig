#fsconfig.py - Webapp for Flussonic Streaming Server mutliple streams configedit

import json
import redis
from redis.commands.json.path import Path
from bottle import route, run, template, request, debug, static_file, error, default_app

choosenChannels = []

allowedIP = ['127.0.0.1', '62.90.52.94', '94.130.136.116', '185.180.103.78']
menuLinks = {'main-menu' : 'MainMenu',
             'choose-channels' : 'ChooseChannels',
             'dvr-settings' : 'DVRSettings',
             'source-priority' : 'SourcePriority',
             'stream-sorting' : 'StreamSorting',
             'config-upload' : 'ConfigUpload',
             'config-download' : 'ConfigDownload'}

redisClient = redis.Redis(host='localhost', port=6379, db=0)

def ConfigLoadUpdate(func):
    def Wrapper():
        uploadedConfig = {}

        uploadedConfig.update(redisClient.json().get('uploadedConfig', Path.root_path()))
        output = func(uploadedConfig)
        redisClient.json().set('uploadedConfig', Path.root_path(), output[1])
        return output[0]

    return Wrapper

@route('/<url>', method=['GET','POST'])
def Router(url):

    if request.environ.get('HTTP_X_FORWARDED_FOR') is not None and request.environ.get('HTTP_X_FORWARDED_FOR') not in allowedIP or request.environ.get('REMOTE_ADDR') not in allowedIP:
        print(request.environ.get('REMOTE_ADDR'))
        return(HTTPErrorHandling(403))

    if url in menuLinks:
        return(globals()[menuLinks[url]]())

    return(HTTPErrorHandling(404))

@route('/')
def RouterWrapper():
        return Router('main-menu')

def HTTPErrorHandling(code):

    if code == 403:
        return('access denied')
    if code == 404:
        return('page doesnt exist')

def MainMenu():
    return template('templates/main_menu.tpl')

def ChooseChannels():

    if request.method == 'GET':
        for stream in redisClient.json().get('uploadedConfig', Path('.streams')):
            channelList.append(stream['name'])
        return template('templates/choose_channels_form.tpl', names = channelList)

    for channel in channelList:
        if request.forms.get(channel) == 'on':
            choosenChannels.append(channel)

    return template('templates/choosen_channels.tpl', names = choosenChannels)

@ConfigLoadUpdate
def DVRSettings(config):

    if request.method == 'GET':
        return template('templates/dvr_settings_form.tpl'), config

    discSpace = int(request.forms.get('space')) * 1024 ** 3
    dvrLimit = int(request.forms.get('duration'))
    dvrRoot = request.forms.get('path')

    for stream in config['streams']:
        if stream['name'] in choosenChannels:
            stream['dvr'] = {"disk_space" : discSpace,
                             "dvr_limit" : dvrLimit,
                             "expiration" : dvrLimit,
                             "root" : dvrRoot,
                             "storage_limit" : discSpace}
            if dvrLimit == 0:
                del stream['dvr']

    return template('templates/dvr_complete.tpl'), config

@ConfigLoadUpdate
def SourcePriority(config):

    if request.method == 'GET':
        return template('templates/source_priority_form.tpl'), config

    firstCondition = request.forms.get('firstCondition')
    firstConditionPriority = request.forms.get('firstConditionPriority')
    secondCondition = request.forms.get('secondCondition')
    secondConditionPriority = request.forms.get('secondConditionPriority')
    defaultPriority = request.forms.get('defaultPriority')

    for stream in config['streams']:
        if stream['name'] in choosenChannels:
            for url in stream['inputs']:
                if firstCondition in url['url'] and firstCondition != '':
                    url['priority'] = firstConditionPriority
                elif secondCondition in url['url'] and secondCondition != '':
                    url['priority'] = secondConditionPriority
                else:
                    url['priority'] = defaultPriority

    return template('templates/source_priority_complete.tpl'), config

@ConfigLoadUpdate
def StreamSorting(config):

    if request.method == 'GET':
        return template('templates/stream_sorting_channels_form.tpl', names = choosenChannels), config

    for stream in config['streams']:
        if stream['name'] in choosenChannels:
            stream['position'] = request.forms.get(stream['name'])

    config['streams'].sort(key=lambda x: int(x.get('position')))

    return template('templates/sorting_complete.tpl'), config

def ConfigUpload():

    if request.method == 'GET':
        return template('templates/upload_file_form.tpl')

    channelList = []

    redisClient.json().set('uploadedConfig', Path.root_path(), json.load(request.files.get('config').file))

    for stream in redisClient.json().get('uploadedConfig', Path('.streams')):
            channelList.append(stream['name'])

    redisClient.set('channelList', channelList)

    return template('templates/upload_complete.tpl')

def ConfigDownload():

    with open('./output_config.json', 'w') as file:
        json.dump(redisClient.json().get('uploadedConfig', Path.root_path()), file)

    return static_file('output_config.json', root='./', download=True)

#def main():
#   run(server='gunicorn', host='10.100.102.6', port=8080)
    #run(host='127.0.0.1', port=8080)

app = default_app()

#if __name__ == '__main__':
#    main()
