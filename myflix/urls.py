"""myflix URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

from myflix.app import views as core_views

urlpatterns = [
    # myflix
    url(r'^$', core_views.index, name='index'),
    url(r'^tiers/$', core_views.tiers, name='tiers'),
    url(r'^servers/$', core_views.servers, name='servers'),
    url(r'^help/$', core_views.help, name='help'),
    url(r'^order/(?P<server_id>\d+)/$', login_required(core_views.order), name='order'),
    url(r'^order/(?P<server_id>\d+)/(?P<tier_id>\d+)/$', login_required(core_views.order_tier), name='order_tier'),
    # account
    url(r'^account/login/$', auth_views.login, name='login', kwargs={'redirect_authenticated_user': True,
                                                                     'template_name': 'account/login.html'}),
    url(r'^account/logout/$', auth_views.logout, {'next_page': 'index'}, name='logout'),
    url(r'^account/register/$', core_views.register, name='register'),
    url(r'^account/profile/$', login_required(core_views.profile), name='profile'),
    # admin
    url(r'^admin/', admin.site.urls),
]
