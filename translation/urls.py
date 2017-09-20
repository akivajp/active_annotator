from django.conf.urls import url

from . import views

app_name = "translation"

urlpatterns = [
    url('^$', views.index, name='index'),
    url('^index/(?P<sort_key>[a-z_]+)/$', views.index, name='index'),
    url('^index/(?P<sort_key>[a-z_]+)/(?P<reverse>0|1)/$', views.index, name='index'),
    url('^create/(?P<model>.*)$', views.create, name='create'),
    url('^edit/(?P<project_id>[0-9]+)$', views.edit, name='edit'),
    url('^edit/(?P<project_id>[0-9]+)/(?P<edit_id>[0-9]+)/$', views.edit, name='edit'),
    url('^preprocess/(?P<project_id>[0-9]+)/$', views.preprocess, name='preprocess'),
    url('^project/(?P<project_id>[0-9]+)/$', views.project, name='project'),
    url('^skip/(?P<translation_id>[0-9]+)/$', views.skip, name='skip'),
    url('^translations/editor/(?P<user_id>[0-9]+)/$', views.translations, name='translations/editor'),
    url('^translations/editor/(?P<user_id>[0-9]+)/(?P<sort_key>[a-z_]+)/$', views.translations, name='translations/editor'),
    url('^translations/editor/(?P<user_id>[0-9]+)/(?P<sort_key>[a-z_]+)/(?P<reverse>0|1)/$', views.translations, name='translations/editor'),
    url('^translations/project/(?P<project_id>[0-9]+)/$', views.translations, name='translations/project'),
    url('^translations/project/(?P<project_id>[0-9]+)/(?P<sort_key>[a-z_]+)/$', views.translations, name='translations/project'),
    url('^translations/project/(?P<project_id>[0-9]+)/(?P<sort_key>[a-z_]+)/(?P<reverse>0|1)/$', views.translations, name='translations/project'),
    url('^update/(?P<model>.*)/(?P<id>[0-9]+)$', views.update, name='update'),
    url('^upload/(?P<model>.*)$', views.upload, name='upload'),
    #url('^project/(?P<project_id>[0-9]+)/$', views.edit, name='project'),
    #url('^skip/(?P<caption_id>[0-9]+)/$', views.skip, name='skip'),
]

# ajax commands
urlpatterns += [
    url('^ajax_delete/(?P<target>[a-z]+)/(?P<id>[0-9]+)/$', views.ajax_delete, name='ajax_delete'),
    url('^ajax_toggle/(?P<target>[a-z]+)/(?P<id>[0-9]+)/$', views.ajax_toggle, name='ajax_toggle'),
]
