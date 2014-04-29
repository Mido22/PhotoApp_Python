from settings import MEDIA_ROOT
from django.conf.urls import patterns, include, url
import ptoApp.views

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', ptoApp.views.goToHomePage),
    url(r'^loginPage/', ptoApp.views.goToLogin),
    url(r'^homepage/', ptoApp.views.homepg),
    (r'^leftSideBar/$', ptoApp.views.leftSideBar),
    (r'^logout/$', ptoApp.views.logout),
    (r'^mainPage/$', ptoApp.views.loadAlbum),
    (r'^createAlbum/$', ptoApp.views.createAlbum),
    (r'^renameAlbum/$', ptoApp.views.renameAlbum),
    (r'^deleteAlbum/$', ptoApp.views.deleteAlbum),
    (r'^loadImage/$', ptoApp.views.loadImage),
    (r'^deletePhotos/$', ptoApp.views.deletePhotos),
    (r'^downloadPhotos/$', ptoApp.views.downloadPhotos),
    (r'^makeCollage/$', ptoApp.views.makeCollage),
    (r'^movePhotos/$', ptoApp.views.movePhotos),

    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': MEDIA_ROOT,}),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
