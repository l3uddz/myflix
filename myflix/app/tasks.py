# Create your tasks here
from __future__ import absolute_import, unicode_literals

import logging

from celery import shared_task, group

from myflix.app.models import PlexServer

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
        plex_server = PlexServer.objects.get(pk=server)
    logger.info("Checking max streams for server %r", plex_server.name)
    return "{name} has no active stream abusers".format(name=plex_server.name)


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
