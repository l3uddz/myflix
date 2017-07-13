import logging

from django import forms
from django.contrib import admin

from myflix.app.models import Profile, PlexServer, PlexTier
from myflix.utils.plex import Plex

logger = logging.getLogger(__name__)


# Form Validators
class PlexServerForm(forms.ModelForm):
    class Meta:
        model = PlexServer
        fields = '__all__'

    def clean(self):
        cleaned_data = super(PlexServerForm, self).clean()
        try:
            name = cleaned_data['name']
            url = cleaned_data['url']
            token = cleaned_data['token']

            # validate server url and token
            server = Plex(name, url, token)
            if not server.validate():
                self.add_error('url', 'Unable to validate the supplied server url')
                self.add_error('token', 'Unable to validate the supplied server token')

        except:
            logger.exception("Exception occurred while validating PlexServerForm: ")
            raise forms.ValidationError("Unable to validate the server url & token provided...")

        return cleaned_data


# Inline models
class ProfileInline(admin.TabularInline):
    model = Profile
    readonly_fields = ['user']
    can_delete = False


class PlexServerAdmin(admin.ModelAdmin):
    inlines = [
        ProfileInline
    ]
    form = PlexServerForm


class PlexTierAdmin(admin.ModelAdmin):
    inlines = [
        ProfileInline
    ]


# Register your models here.
admin.site.register(Profile)
admin.site.register(PlexServer, PlexServerAdmin)
admin.site.register(PlexTier, PlexTierAdmin)
