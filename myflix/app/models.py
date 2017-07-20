import logging

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from djmoney.models.fields import MoneyField

logger = logging.getLogger(__name__)


# plex models
class PlexTier(models.Model):
    name = models.CharField(max_length=30, verbose_name="Tier Name")
    max_streams = models.IntegerField(default=1, verbose_name="Tier max allowed concurrent user streams")
    allowed_sync = models.BooleanField(default=False, verbose_name="Allow offline syncs")
    allowed_transcodes = models.BooleanField(default=True, verbose_name="Allow transcodes")
    allowed_paused = models.BooleanField(default=True, verbose_name="Allow stream pauses")
    price = MoneyField(max_digits=10, decimal_places=2, default=10, default_currency='USD',
                       verbose_name="Tier price")
    description = models.TextField(verbose_name="Tier Description")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Plex Tier'


class PlexServer(models.Model):
    name = models.CharField(max_length=30, verbose_name="Server Name")
    url = models.URLField(verbose_name="Server URL")
    token = models.CharField(max_length=30, verbose_name="Plex Token with administrator rights")
    max_subscribers = models.IntegerField(default=10, verbose_name="Maximum subscribers for this server")
    tiers = models.ManyToManyField(PlexTier, verbose_name="Tiers this server allows")

    def __str__(self):
        return self.name

    def available_slots(self):
        users = Profile.objects.filter(server=self.pk)
        current_subscribers = 0
        for user in users:
            current_subscribers += user.tier.max_streams
        available = self.max_subscribers - current_subscribers
        return available if available else 0

    class Meta:
        verbose_name_plural = 'Plex Server'


# user models
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="User this profile belongs too")
    server = models.ForeignKey(PlexServer, null=True, blank=True, on_delete=models.SET_NULL,
                               verbose_name="Server subscribed too")
    tier = models.ForeignKey(PlexTier, null=True, blank=True, on_delete=models.SET_NULL,
                             verbose_name="Tier subscribed too")
    join_date = models.DateTimeField(auto_now_add=True, blank=True, verbose_name="Join date")
    last_seen = models.DateTimeField(blank=True, null=True, verbose_name="Last plex stream")
    subscription_expires = models.DateTimeField(null=True, blank=True, verbose_name="Subscription expires date")
    plex_name = models.CharField(max_length=64, blank=True, verbose_name="Plex username")

    def __str__(self):
        return self.user.username


# app models
class News(models.Model):
    user = models.ManyToManyField(User, verbose_name="Poster of news article")
    title = models.CharField(max_length=256, verbose_name="Article title")
    content = models.TextField(verbose_name="Article content")
    pub_date = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'News'


# receivers

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
