# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=maybe-no-member


import secrets
import logging
from bottle import route, request, default_app, response
from controllers import (
    direct_api_query, main_menu, choose_channels, dvr_settings, source_priority, stream_sorting,
    load_config_file_json, download_config_file_json, config_upload_to_server_api,
    config_load_from_server_api
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


ALLOWED_IP = ['127.0.0.1', '62.90.52.94', '94.130.136.116', '10.100.102.6', '10.100.102.30']
menu_links = {'main-menu' : main_menu,
              'choose-channels' : choose_channels,
              'direct-api-query' : direct_api_query,
              'dvr-settings' : dvr_settings,
              'source-priority' : source_priority,
              'stream-sorting' : stream_sorting,
              'config-load-json' : load_config_file_json,
              'config-download-json' : download_config_file_json,
              'config-upload-api' : config_upload_to_server_api,
              'config-load-api' : config_load_from_server_api}


@route('/<url>', method=['GET','POST'])
def router(url: str):

    #if (request.environ.get('HTTP_X_FORWARDED_FOR') is not None  \
    #    and request.environ.get('HTTP_X_FORWARDED_FOR') not in ALLOWED_IP)  \
    #    or request.environ.get('REMOTE_ADDR') not in ALLOWED_IP:

    #    logger.info(request.environ.get('REMOTE_ADDR'))
    #    logger.info(request.environ.get('HTTP_X_FORWARDED_FOR'))
    #    return http_error_handling(403)

    logger.info('REMOTE_ADDR : %s', request.environ.get('REMOTE_ADDR'))
    logger.info('FORWARDED : %s', request.environ.get('HTTP_X_FORWARDED_FOR'))

    session_id = request.get_cookie('sessionid')
    logger.info('Session ID : %s', session_id)

    if session_id is None:
        session_id = secrets.token_urlsafe(8)
        response.set_cookie('sessionid', session_id)

    if url in menu_links:
        return menu_links[url](session_id)

    return http_error_handling(404)


@route('/')
def router_wrapper():
    return router('main-menu')


def http_error_handling(code: int) -> str:

    if code == 403:
        return 'access denied'

    if code == 404:
        return "page doesn't exist"

    return 'routing error'


app = default_app()
