from django.contrib import admin

from myflix.app.models import Profile, PlexServer, PlexTier


# Inline models
class ProfileInline(admin.TabularInline):
    model = Profile
    readonly_fields = ['user']
    can_delete = False


class PlexServerAdmin(admin.ModelAdmin):
    inlines = [
        ProfileInline
    ]


class PlexTierAdmin(admin.ModelAdmin):
    inlines = [
        ProfileInline
    ]


# Register your models here.
admin.site.register(Profile)
admin.site.register(PlexServer, PlexServerAdmin)
admin.site.register(PlexTier, PlexTierAdmin)
