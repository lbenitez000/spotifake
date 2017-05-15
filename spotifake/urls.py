"""sample URL Configuration

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
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import ObtainAuthToken

from music.views import ArtistAPIView, ArtistItemAPIView, AlbumAPIView, AlbumItemAPIView, TrackItemAPIView

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^api/auth/$$', ObtainAuthToken.as_view(), name='api_auth'),
    url(r'^api/artist/$', ArtistAPIView.as_view(), name='api_artist'),
    url(r'^api/artist/(?P<pk>\d+)/$', ArtistItemAPIView.as_view(), name='api_artist_item'),
    url(r'^api/album/$', AlbumAPIView.as_view(), name='api_album'),
    url(r'^api/artist/(?P<artist_id>\d+)/album/$', AlbumAPIView.as_view(), name='api_artist_item_album'),
    url(r'^api/album/(?P<pk>\d+)/$', AlbumItemAPIView.as_view(), name='api_album_item'),
    url(r'^api/track/(?P<pk>\d+)/$', TrackItemAPIView.as_view(), name='api_track_item'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
