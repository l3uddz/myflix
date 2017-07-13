import logging
import platform
from urllib.parse import urljoin
from uuid import getnode

import requests

logger = logging.getLogger(__name__)


class Plex:
    def __init__(self, name, url, token):
        self.name = name
        self.url = url
        self.token = token

    def validate(self):
        request_url = urljoin(self.url, 'status/sessions')
        headers = {
            'X-Plex-Token': self.token,
            'Accept': 'application/json',
            'X-Plex-Provides': 'controller',
            'X-Plex-Platform': platform.uname()[0],
            'X-Plex-Platform-Version': platform.uname()[2],
            'X-Plex-Product': 'myflix',
            'X-Plex-Version': '0.9.5',
            'X-Plex-Device': platform.platform(),
            'X-Plex-Client-Identifier': str(hex(getnode()))
        }

        try:
            r = requests.get(request_url, headers=headers, verify=False)
            if r.status_code == 200 and r.headers['Content-Type'] == 'application/json':
                logger.info("Server url and token were valid!")
                logger.debug("Server responded with status_code=%r, content: %r", r.status_code, r.json())
                return True
            else:
                logger.info("Server url or token were invalid...")
                logger.debug("Server responded with status_code=%r, content: %r", r.status_code, r.content)
                return False
        except:
            logger.exception("Exception validating server token=%r, url=%r: ", self.token, self.url)
            return False

    def get_streams(self):
        request_url = urljoin(self.url, 'status/sessions')
        headers = {
            'X-Plex-Token': self.token,
            'Accept': 'application/json',
            'X-Plex-Provides': 'controller',
            'X-Plex-Platform': platform.uname()[0],
            'X-Plex-Platform-Version': platform.uname()[2],
            'X-Plex-Product': 'myflix',
            'X-Plex-Version': '0.9.5',
            'X-Plex-Device': platform.platform(),
            'X-Plex-Client-Identifier': str(hex(getnode()))
        }

        try:
            r = requests.get(request_url, headers=headers, verify=False)
            if r.status_code == 200 and r.headers['Content-Type'] == 'application/json':
                result = r.json()
                if 'MediaContainer' not in result:
                    logger.error("Failed to retrieve streams from server %r", self.name)
                    return None
                elif 'Video' not in result['MediaContainer']:
                    logger.info("There were no streams to check for server %r", self.name)
                    return []

                streams = []
                for stream in result['MediaContainer']['Video']:
                    streams.append(PlexStream(stream))
                return streams

            else:
                logger.error(
                    "Server url or token was invalid, token=%r, request_url=%r, status_code=%r, content: %r",
                    self.token, request_url, r.status_code, r.content)
                return None
        except:
            logger.exception("Exception retrieving streams from request_url=%r, token=%r: ", request_url,
                             self.token)
            return None

    def kill_stream(self, session_id, reason):
        request_url = urljoin(self.url, 'status/sessions/terminate')
        headers = {
            'X-Plex-Token': self.token
        }
        payload = {
            'sessionId': session_id,
            'reason': reason
        }
        try:
            r = requests.get(request_url, headers=headers, params=payload, verify=False)
            if r.status_code == 200:
                return True
            else:
                return False
        except:
            logger.exception("Exception killing stream %r: ", session_id)
            return False


# helper classes (parsing responses etc...)
class PlexStream:
    def __init__(self, stream):
        self.user = stream['User']['title']
        self.player = stream['Player']['title']
        self.session_id = stream['Session']['id']
        self.media_title = self.get_stream_filename(stream)
        self.stream_state = stream['Player']['state']
        self.stream_type = stream['Media']['Part']['decision']

    def __str__(self):
        return "{user} is playing {media} using {player}. " \
               "Stream state: {state}, type: {type}. Session key: {session}".format(user=self.user,
                                                                                    media=self.media_title,
                                                                                    player=self.player,
                                                                                    state=self.stream_state,
                                                                                    type=self.stream_type,
                                                                                    session=self.session_id)

    def __getattr__(self, item):

        try:
            return self.__getattribute__(item)
        except AttributeError:
            pass

        # Default behaviour
        return 'Unknown'

    @staticmethod
    def get_stream_filename(stream):
        filename = "Unknown"
        if stream['title'] is None:
            return filename

        if stream['type'] == 'episode':
            filename = "{} {}x{}".format(stream['grandparentTitle'], stream['parentIndex'], stream['index'])
        else:
            filename = stream['title']
        return filename
