# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import date

from rest_framework.generics import ListCreateAPIView,RetrieveUpdateAPIView,  RetrieveUpdateDestroyAPIView

from music.models import Artist, Album, Track
from music.serializers import ArtistWithRelationsSerializer, AlbumSerializer, TrackSerializer


class ArtistAPIView(ListCreateAPIView):
     serializer_class = ArtistWithRelationsSerializer
     queryset = Artist.objects.all()


class ArtistItemAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = ArtistWithRelationsSerializer
    queryset = Artist.objects.all()


class AlbumAPIView(ListCreateAPIView):
    serializer_class = AlbumSerializer

    def get_queryset(self):
        # Get the base queryset
        queryset = Album.objects.all()

        # Apply filters
        # By artist
        artist_id = self.kwargs.get('artist_id')
        if artist_id:
            queryset = queryset.filter(artist_id=artist_id)
        # Hide unreleased albums from non-admin users
        if not self.request.user.is_staff:
            queryset = queryset.filter(release_date__lte=date.today())

        return queryset


class AlbumItemAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = AlbumSerializer

    def get_queryset(self):
        # Get the base queryset
        queryset = Album.objects.all()

        # Apply filters
        # Hide unreleased albums from non-admin users
        if not self.request.user.is_staff:
            queryset = queryset.filter(release_date__lte=date.today())

        return queryset


class TrackItemAPIView(RetrieveUpdateAPIView):
    serializer_class = TrackSerializer

    def get_queryset(self):
        # Get the base queryset
        queryset = Track.objects.all()

        # Apply filters
        # Hide unreleased tracks from non-admin users
        if not self.request.user.is_staff:
            queryset = queryset.filter(album__release_date__lte=date.today())

        return queryset