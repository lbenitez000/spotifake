from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from drf_extra_fields.fields import Base64ImageField

from music.models import Artist, Album, Track
from spotifake.fields import AudioField

class ArtistWithRelationsSerializer(serializers.ModelSerializer):
    """Serializes an Artist including a list of related artists generated dynamically"""

    related_artists = serializers.SerializerMethodField()

    def get_related_artists(self, artist):
        """Get artists the current artist has collaborated with"""
        tracks_as_collaborator = artist.collaborations.prefetch_related('artist')
        tracks_with_collaborators = artist.tracks.prefetch_related('collaborators')
        artists_collaborated = [track.artist for track in tracks_as_collaborator]
        artists_collaborators = []
        for track in tracks_with_collaborators.all():
            artists_collaborators.extend(track.collaborators.all())
        related_artists = set()
        related_artists.update(artists_collaborated)
        related_artists.update(artists_collaborators)
        related_artist_serializer = ArtistSerializer(related_artists, many=True)
        return related_artist_serializer.data

    class Meta:
        model = Artist
        fields = ('id', 'name', 'related_artists')
        wrapper_name = 'artists'


class ArtistSerializer(serializers.ModelSerializer):

    class Meta:
        model = Artist
        fields = ('id', 'name')


class TrackSerializer(serializers.ModelSerializer):

    audio = AudioField()
    collaborators = serializers.PrimaryKeyRelatedField(queryset=Artist.objects.all(), many=True, required=False)

    class Meta:
        model = Track
        fields = ('id', 'index', 'collaborators', 'name', 'audio')
        wrapper_name = 'tracks'


class AlbumSerializer(serializers.ModelSerializer):

    cover = Base64ImageField()
    # List of collaborators in the tracks of the album
    collaborators = serializers.SerializerMethodField()
    # Number of thracks in the album
    n_tracks = serializers.SerializerMethodField()
    # The list of tracks
    tracks = TrackSerializer(many=True)

    def get_collaborators(self, album):
        collaborators = set()
        for song in album.tracks.all():
            collaborators.update(song.collaborators.all())
        collaborators_ids = [collaborator.id for collaborator in collaborators]
        return collaborators_ids

    def get_n_tracks(self, album):
        return album.tracks.count()

    def create(self, validated_data):

        tracks_kwargs = validated_data.pop('tracks')

        with transaction.atomic():
            # Create the album
            album = Album.objects.create(**validated_data)
            # Create the tracks related to the current album
            for track_kwargs in tracks_kwargs:
                collaborators = track_kwargs.pop('collaborators', None)
                track = Track.objects.create(artist=album.artist, album=album, **track_kwargs)
                # Add the collaborators
                if collaborators:
                    track.collaborators.add(*collaborators)

        return album

    class Meta:
        model = Album
        fields = ('id', 'artist', 'collaborators', 'name', 'release_date', 'cover', 'n_tracks', 'tracks')
        wrapper_name = 'albums'
