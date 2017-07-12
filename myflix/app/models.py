from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from djmoney.models.fields import MoneyField


# plex models
class PlexTier(models.Model):
    name = models.CharField(max_length=30, verbose_name="Tier Name")
    max_streams = models.IntegerField(default=1, verbose_name="Maximum concurrent streams per user for this tier")
    allowed_sync = models.BooleanField(default=False, verbose_name="Is sync allowed")
    price = MoneyField(max_digits=10, decimal_places=2, default=10, default_currency='USD',
                       verbose_name="How much is this tier")

    def __str__(self):
        return self.name


class PlexServer(models.Model):
    name = models.CharField(max_length=30, verbose_name="Plex Server Name")
    url = models.URLField(verbose_name="Full Server URL")
    token = models.CharField(max_length=30, verbose_name="Plex Token with administrator rights")
    max_subscribers = models.IntegerField(default=10, verbose_name="Maximum subscribers for this server")
    tiers = models.ManyToManyField(PlexTier, verbose_name="Tiers this server allows")

    def __str__(self):
        return self.name


# user models
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="User this profile is for")
    server = models.OneToOneField(PlexServer, null=True, blank=True, on_delete=models.SET_NULL,
                                  verbose_name="Server this user is subscribed too")
    tier = models.OneToOneField(PlexTier, null=True, blank=True, on_delete=models.SET_NULL,
                                verbose_name="Tier this user is subscribed too")

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
