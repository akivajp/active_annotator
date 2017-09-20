#from django.conf.urls import include
from django.conf.urls import url
#from django.contrib import admin
from django.contrib.auth.views import login

from . import views

app_name = 'accounts'

urlpatterns = [
    #url(r'^admin/', include(admin.site.urls)),
    #url(r'^login/$', login, name='login'),
    url(r'^login/$', login,
        {'template_name': 'accounts/login.html'},
        name='login'),
    url(r'^logout/$', views.logout, name='logout'),
]

