#fsconfig.py - Webapp for Flussonic mutliple streams config file edit

import json
from bottle import route, run, template, request, debug, static_file, error

uploadedConfig = {}
channelList = []
choosenChannels = []

allowedIP = ['127.0.0.1', '62.90.52.94', '94.130.136.116']
menuLinks = {'main-menu' : 'MainMenu',
             'choose-channels' : 'ChooseChannels',
             'dvr-settings' : 'DVRSettings',
             'source-priority' : 'SourcePriority',
             'stream-sorting' : 'StreamSorting',
             'config-upload' : 'ConfigUpload',
             'config-download' : 'ConfigDownload'}

@route('/<url>', method=['GET','POST'])
def Router(url):

    if request.environ.get('HTTP_X_FORWARDED_FOR') is not None and request.environ.get('HTTP_X_FORWARDED_FOR') not in allowedIP or request.environ.get('REMOTE_ADDR') not in allowedIP:
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
        return template('templates/choose_channels_form.tpl', names = channelList)

    for channel in channelList:
        if request.forms.get(channel) == 'on':
            choosenChannels.append(channel)

    return template('templates/choosen_channels.tpl', names = choosenChannels)

def DVRSettings():

    if request.method == 'GET':
        return template('templates/dvr_settings_form.tpl')

    discSpace = int(request.forms.get('space')) * 1024 ** 3
    dvrLimit = int(request.forms.get('duration'))
    dvrRoot = request.forms.get('path')

    for stream in uploadedConfig['streams']:
        if stream['name'] in choosenChannels:
            stream['dvr'] = {"disk_space": discSpace,
                             "dvr_limit":dvrLimit,
                             "expiration":dvrLimit,
                             "root":dvrRoot,
                             "storage_limit":discSpace}
            if dvrLimit == 0:
                del stream['dvr']

    return template('templates/dvr_complete.tpl')

def SourcePriority():

    if request.method == 'GET':
        return template('templates/source_priority_form.tpl')

    firstCondition = request.forms.get('firstCondition')
    firstConditionPriority = request.forms.get('firstConditionPriority')
    secondCondition = request.forms.get('secondCondition')
    secondConditionPriority = request.forms.get('secondConditionPriority')
    defaultPriority = request.forms.get('defaultPriority')

    for stream in uploadedConfig['streams']:
        if stream['name'] in choosenChannels:
            for url in stream['inputs']:
                if firstCondition in url['url'] and firstCondition != '':
                    url['priority'] = firstConditionPriority
                elif secondCondition in url['url'] and secondCondition != '':
                    url['priority'] = secondConditionPriority
                else:
                    url['priority'] = defaultPriority

    return template('templates/source_priority_complete.tpl')

def StreamSorting():

    if request.method == 'GET':
        return template('templates/stream_sorting_channels_form.tpl', names = choosenChannels)

    for stream in uploadedConfig['streams']:
        if stream['name'] in choosenChannels:
            stream['position'] = request.forms.get(stream['name'])

    uploadedConfig['streams'].sort(key=lambda x: int(x.get('position')))

    return template('templates/sorting_complete.tpl')

def ConfigUpload():

    if request.method == 'GET':
        return template('templates/upload_file_form.tpl')

    #try:
    uploadedConfig.update(json.load(request.files.get('config').file))
    #
    #except:
    #    raise ValueError

    for stream in uploadedConfig['streams']:
       channelList.append(stream['name'])

    return template('templates/upload_complete.tpl')

def ConfigDownload():

    with open('./output_config.json', 'w') as file:
        json.dump(uploadedConfig, file)

    return static_file('output_config.json', root='./', download=True)

def main():

    debug(True)
    run(host='10.100.102.6', port=8080)
    #run(host='127.0.0.1', port=8080)

if __name__ == '__main__':
    main()