#FSConfig.py - Webface for Flussonic config file edit
#Autodeploytest

import json
from bottle import route, run, template, request, debug, static_file, error

uploadedConfig = {}
channelList = []
choosenChannels = []

@route('/')
def main_menu():
    return template('views/main_menu.tpl')

@route('/choose-channels')
def ShowChannelsListForm():
    return template('views/choose_channels_form.tpl', names = channelList)

@route('/choose-channels', method='POST')
def ChooseChannels():

    #global choosenChannels

    for channel in channelList:
        if request.forms.get(channel) == 'on':
            choosenChannels.append(channel)

    return template('views/choosen_channels.tpl', names = choosenChannels)

@route('/dvr-settings')
def DVRSettings():
    return template('views/dvr_settings_form.tpl')

@route('/dvr-settings', method='POST')
def DVRSettings():

    #global uploadedConfig

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

    return template('views/dvr_complete.tpl')

@route('/source-priority')
def ShowSourcePriorityForm():
    return template('views/source_priority_form.tpl')

@route('/source-priority', method='POST')
def SourcePriority():

    #global UploadedConfig

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

    return template('views/source_priority_complete.tpl')

@route('/stream-sorting')
def ShowStreamSortingForm():
    return template('views/stream_sorting_channels_form.tpl', names = choosenChannels)

@route('/stream-sorting', method='POST')
def StreamSorting():

    #global UploadedConfig

    for stream in uploadedConfig['streams']:
        if stream['name'] in choosenChannels:
            stream['position'] = request.forms.get(stream['name'])

    uploadedConfig['streams'].sort(key=lambda x: int(x.get('position')))

    return template('views/sorting_complete.tpl')

@route('/config-upload')
def ShowUploadForm():
    return template('views/upload_file_form.tpl')

@route('/config-upload', method='POST')
def ConfigUpload():

    #global uploadedConfig
    #global channelList

    #try:
    uploadedConfig = json.load(request.files.get('config').file)
    #
    #except:
    #    raise ValueError

    for stream in uploadedConfig['streams']:
       channelList.append(stream['name'])

    return template('views/upload_complete.tpl')

@route('/config-download')
def ConfigDownload():

    with open('./output_config.json', 'w') as file:
        json.dump(uploadedConfig, file)

    return static_file('output_config.json', root='./', download=True)

@error(404)
def HTTPErrorHandling(code):
    return template('views/http_error.tpl')

def main():

    debug(True)
    run(host='10.100.102.6', port=8080)

if __name__ == '__main__':
    main()
