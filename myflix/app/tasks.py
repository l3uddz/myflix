# Create your tasks here
from __future__ import absolute_import, unicode_literals

import logging

from celery import shared_task, group

from myflix.app.models import PlexServer
from myflix.utils.plex import Plex, PlexStream

logger = logging.getLogger(__name__)


############################################################
# SINGULAR TASKS
############################################################
@shared_task(server=None)
def plex_check_server_max_streams(server=None):
    if not server:
        logger.error("The server supplied was not valid, skipping...")
        raise Exception("Invalid server_pk was supplied")
    else:
        server_object = PlexServer.objects.get(pk=server)
    logger.info("Checking max streams for server %r", server_object.name)

    # retrieve active stream sessions
    plex_server = Plex(server_object.name, server_object.url, server_object.token)
    streams = plex_server.get_streams()
    if not streams or 'MediaContainer' not in streams:
        logger.error("Failed to retrieve streams from server %r", plex_server.name)
        raise Exception("Unable to retrieve streams from server: {name}".format(name=plex_server.name))
    elif 'Video' not in streams['MediaContainer']:
        logger.info("There were no streams to check for server: {name}".format(name=plex_server.name))
        logger.debug(streams)
        return "There were no active streams for server: {name}".format(name=plex_server.name)

    # process stream list
    for stream in streams['MediaContainer']['Video']:
        stream_info = PlexStream(stream)
        logger.debug("Stream: %s", stream_info)
        if stream_info.stream_state == 'paused':
            if plex_server.kill_stream(stream_info.session_id, 'No paused streams are allowed'):
                logger.debug("Killed stream because it was paused!")
            else:
                logger.debug("Problem killing stream....")

    return "{name} has no active stream abusers".format(name=server_object.name)


############################################################
# MANAGER TASKS
############################################################
@shared_task()
def manager_check_max_streams():
    plex_servers = PlexServer.objects.all()
    if plex_servers.count():
        logger.debug("Checking %d plex servers", plex_servers.count())
        g = group([plex_check_server_max_streams.s(p.pk) for p in plex_servers])
        g.apply_async()
        return "Queued {server_count} servers to have their max_streams checked".format(
            server_count=plex_servers.count())
    return "There were no servers to have their max_streams checked"
