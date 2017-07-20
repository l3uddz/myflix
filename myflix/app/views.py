from django import forms
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
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
    return render(request, 'account/profile.html', {'form': form})


# Forms
class UserCreateForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserCreateForm, self).__init__(*args, **kwargs)

        for field in ['username', 'password1', 'password2']:
            self.fields[field].help_text = None


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ['user']
