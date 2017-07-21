from django import forms
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect

from myflix.app.models import PlexTier, PlexServer, News, Profile


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
    news_articles = News.objects.all().order_by('-id')[:5]
    plex_servers = PlexServer.objects.all()
    return render(request, 'core/help.html', {'news': news_articles, 'servers': plex_servers})


def register(request):
    if request.user.is_authenticated():
        return redirect('profile')

    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('profile')
    else:
        form = UserCreateForm()
    return render(request, 'account/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
    else:
        form = ProfileForm(instance=request.user.profile)
    return render(request, 'account/profile.html', {'form': form, 'profile': request.user.profile})


@login_required
def order(request, server_id):
    server = get_object_or_404(PlexServer, pk=server_id)
    return render(request, 'core/order.html', {'server': server})


@login_required
def order_tier(request, server_id, tier_id):
    server = get_object_or_404(PlexServer, pk=server_id)
    tier = get_object_or_404(PlexTier, pk=tier_id)
    if tier not in server.tiers.all():
        return render(request, 'core/order_tier.html', {'server': None, 'tier': None})
    if server.available_slots() < tier.max_streams:
        return render(request, 'core/order_tier.html', {'server': None, 'tier': None})
    return render(request, 'core/order_tier.html', {'server': server, 'tier': tier})


# Forms
class UserCreateForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserCreateForm, self).__init__(*args, **kwargs)

        for field in ['username', 'password1', 'password2']:
            self.fields[field].help_text = None


class ProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['server'].widget.attrs['disabled'] = True
        self.fields['tier'].widget.attrs['disabled'] = True

    class Meta:
        model = Profile
        exclude = ['user']
