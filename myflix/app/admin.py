import logging

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

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
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'


class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline]

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


class TabuluarProfileInline(admin.TabularInline):
    model = Profile
    readonly_fields = ['user']
    can_delete = False


class PlexServerAdmin(admin.ModelAdmin):
    inlines = [
        TabuluarProfileInline
    ]
    form = PlexServerForm


class PlexTierAdmin(admin.ModelAdmin):
    inlines = [
        TabuluarProfileInline
    ]


# Register your models here.
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(PlexServer, PlexServerAdmin)
admin.site.register(PlexTier, PlexTierAdmin)
