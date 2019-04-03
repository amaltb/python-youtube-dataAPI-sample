from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from log import logger

_API_VERSION = 'v3'


def get_authenticated_service(_client_secret_file, _api_service_name, _app_scope):
    logger.info('Authorization service: ' + _api_service_name)
    try:
        flow = InstalledAppFlow.from_client_secrets_file(_client_secret_file, _app_scope)
        credentials = flow.run_console()
        return build(_api_service_name, _API_VERSION, credentials=credentials)
    except Exception as e:
        raise RuntimeError('Could not authenticate given service...' + str(e))
