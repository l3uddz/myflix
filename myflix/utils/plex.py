import logging
import platform
from urllib.parse import urljoin
from uuid import getnode

import requests

logger = logging.getLogger(__name__)


def validate_server_token(url, token):
    logger.info("Validating url %r, token %r", url, token)
    try:
        check_url = urljoin(url, 'status/sessions')
        headers = {
            'X-Plex-Token': token,
            'Accept': 'application/json',
            'X-Plex-Provides': 'controller',
            'X-Plex-Platform': platform.uname()[0],
            'X-Plex-Platform-Version': platform.uname()[2],
            'X-Plex-Product': 'myflix',
            'X-Plex-Version': '0.9.5',
            'X-Plex-Device': platform.platform(),
            'X-Plex-Client-Identifier': str(hex(getnode()))
        }

        r = requests.get(check_url, headers=headers, verify=False)
        if r.status_code == 200:
            logger.info("Server url and token were valid!")
            logger.debug("Server responded with status code: %r, content: %r", r.status_code, r.json())
            return True
        else:
            logger.info("Server url or token were invalid...")
            logger.debug("Server responded with status code: %r, content: %r", r.status_code, r.content)
            return False
    except:
        logger.exception("Exception validating server token %r", token)
        return False
