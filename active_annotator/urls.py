"""active_annotator URL Configuration

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

from django.conf import settings
from django.conf.urls import include
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.utils.translation import ugettext_lazy
from django.views.generic.base import RedirectView

#from mt_annotate.views import index
from translation.views import index

admin.site.site_header = ugettext_lazy('Active Annotator Administration')
admin.site.site_title  = ugettext_lazy('Active Annotator')

urlpatterns = [
    # root
    url(r'^$', index, name='index'),
    url(r'^index.html$', index, name='index'),
    # apps
    url(r'^accounts/', include('accounts.urls')),
    url(r'^admin/', admin.site.urls),
    #url(r'^mt_annotate/', include('mt_annotate.urls')),
    #url(r'^mt_manage/', include('mt_manage.urls')),
    url(r'^translation/', include('translation.urls')),
    # aliases
    #url(r'^annotate/(?P<sub>.*)', RedirectView.as_view(url='/mt_annotate/%(sub)s', permanent=False)),
    #url(r'^manage/(?P<sub>.*)',   RedirectView.as_view(url='/mt_manage/%(sub)s',   permanent=False)),
]

urlpatterns += static(settings.MEDIA_DIR, document_root=settings.MEDIA_ROOT)
#urlpatterns += static(settings.STATIC_DIR, document_root=settings.STATIC_ROOT)

