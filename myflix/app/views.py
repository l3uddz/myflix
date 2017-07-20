from django.shortcuts import render

from myflix.app.models import PlexTier, PlexServer


# Create your views here.
def index(request):
    return render(request, 'core/index.html')


def tiers(request):
    plex_tiers = PlexTier.objects.all()
    return render(request, 'core/tiers.html', {'tiers': plex_tiers})


def servers(request):
    plex_servers = PlexServer.objects.all()
    return render(request, 'core/servers.html', {'servers': plex_servers})


def help(request):
    return render(request, 'core/help.html')
