# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64

from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.test import APITestCase
from dateutil.parser import parse as parse_ISO8601

from music.models import Artist, Album, Track

User = get_user_model()


class AuthenticationTestCase(APITestCase):

    url = reverse('api_auth')

    users_kwargs = {
        'admin': {
            'username': 'admin',
            'password': 'asdasdasd',
            'is_staff': True
        },
        'user': {
            'username': 'user',
            'password': 'qweqweqwe',
            'is_staff': False
        }
    }

    def setUp(self):

        # Create users
        admin = User.objects.create_user(**self.users_kwargs['admin'])
        user = User.objects.create_user(**self.users_kwargs['user'])

        # Shared data
        self.admin = admin
        self.user = user

    def test_authenticate_admin(self):
        """Authenticate a privileged user"""
        payload = {
            'username': self.users_kwargs['admin']['username'],
            'password': self.users_kwargs['admin']['password'],
        }

        response = self.client.post(self.url, data=payload, format='json')

        # Status
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # In
        self.assertIn('token', response.data)
        # Type
        self.assertRegexpMatches(response.data['token'], r"[a-f0-9]{40}")

    def test_authenticate_user(self):
        """Authenticate an unprivileged user"""
        payload = {
            'username': self.users_kwargs['user']['username'],
            'password': self.users_kwargs['user']['password'],
        }

        response = self.client.post(self.url, data=payload, format='json')

        # Status
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # In
        self.assertIn('token', response.data)
        # Type
        self.assertRegexpMatches(response.data['token'], r"[a-f0-9]{40}")

    def test_authentication_wrong_username(self):
        """Authenticate a user using wrong credentials"""
        payload = {
            'username': self.users_kwargs['user']['username'] + "asdf",
            'password': self.users_kwargs['user']['password'],
        }

        response = self.client.post(self.url, data=payload, format='json')

        # Status
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_authentication_wrong_password(self):
        """Authenticate a user using wrong credentials"""
        payload = {
            'username': self.users_kwargs['user']['username'],
            'password': self.users_kwargs['user']['password'] + "asdf",
        }

        response = self.client.post(self.url, data=payload, format='json')

        # Status
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_authentication_wrong_username_and_password(self):
        """Authenticate a user using wrong credentials"""
        payload = {
            'username': self.users_kwargs['user']['username'] + "asdf",
            'password': self.users_kwargs['user']['password'] + "asdf",
        }

        response = self.client.post(self.url, data=payload, format='json')

        # Status
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class BaseUsersTestCase(APITestCase):
    """A test class for tests which need created users"""

    users_kwargs = {
        'admin': {
            'username': 'admin',
            'password': 'asdasdasd',
            'is_staff': True
        },
        'user': {
            'username': 'user',
            'password': 'qweqweqwe',
            'is_staff': False
        }
    }

    def setUp(self):
        # Create users
        admin = User.objects.create_user(**self.users_kwargs['admin'])
        user = User.objects.create_user(**self.users_kwargs['user'])
        # Create tokens
        Token.objects.create(user=admin)
        Token.objects.create(user=user)

        # Shared data
        self.admin = admin
        self.user = user

        self.admin_token = admin.auth_token.key
        self.user_token = user.auth_token.key


class CreateArtistTestCase(BaseUsersTestCase):

    url = reverse('api_artist')

    artist_payload = {
        'name': "Guns N' Roses",
    }

    def test_create_artist(self):
        """Create an artist as a privileged user"""

        # Test admin user creating an artist
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token)
        response = self.client.post(self.url, data=self.artist_payload, format='json')

        # Status
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # In
        self.assertIn('id', response.data)
        self.assertIn('name', response.data)
        self.assertIn('related_artists', response.data)
        # Type
        self.assertIsInstance(response.data['id'], int)
        self.assertIsInstance(response.data['name'], basestring)
        self.assertIsInstance(response.data['related_artists'], list)
        # Content
        self.assertEqual(response.data['name'], self.artist_payload['name'])
        self.assertEqual(response.data['related_artists'], [])

    def test_create_artist_unauthorized(self):
        """Create an artist as an unauthenticated user"""

        response = self.client.post(self.url, data=self.artist_payload, format='json')

        # Status
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_artist_forbidden(self):
        """Create an artist as an unprivileged user"""

        # Test normal user creating an artist
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token)
        response = self.client.post(self.url, data=self.artist_payload, format='json')

        # Status
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class BaseArtistTestCase(APITestCase):
    """A test class for tests which need a created artist"""

    users_kwargs = {
        'admin': {
            'username': 'admin',
            'password': 'asdasdasd',
            'is_staff': True
        },
        'user': {
            'username': 'user',
            'password': 'qweqweqwe',
            'is_staff': False
        }
    }

    artist_kwargs = {
        'name': "Guns N' Roses"
    }

    def setUp(self):

        # Create users
        admin = User.objects.create_user(**self.users_kwargs['admin'])
        user = User.objects.create_user(**self.users_kwargs['user'])
        # Create tokens
        Token.objects.create(user=admin)
        Token.objects.create(user=user)

        # Shared data
        self.admin = admin
        self.user = user

        self.admin_token = admin.auth_token.key
        self.user_token = user.auth_token.key

    def create_artist(self):
        # Create artist
        Artist.objects.create(**self.artist_kwargs)


class ListArtistTestCase(BaseArtistTestCase):

    url = reverse('api_artist')

    def test_list_artists_as_admin_empty(self):
        """Get an empty list of artists as a privileged user"""

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token)
        response = self.client.get(self.url)

        # Status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Type
        self.assertIsInstance(response.data, list)
        # Content
        self.assertEqual(response.data, [])

    def test_list_artists_as_user_empty(self):
        """Get an empty list of artists as an unprivileged user"""

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token)
        response = self.client.get(self.url)

        # Status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Type
        self.assertIsInstance(response.data, list)
        # Content
        self.assertEqual(response.data, [])

    def test_list_artists_as_admin_nonempty(self):
        """Get an nonempty list of artists as a privileged user"""

        # Create artist
        self.create_artist()

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token)
        response = self.client.get(self.url)

        # Status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Type
        self.assertIsInstance(response.data, list)
        # Content
        self.assertEqual(len(response.data), 1)

        # Type
        self.assertIsInstance(response.data[0], dict)
        # In
        self.assertIn('id', response.data[0])
        self.assertIn('name', response.data[0])
        self.assertIn('related_artists', response.data[0])

        # Type
        self.assertIsInstance(response.data[0]['id'], int)
        self.assertIsInstance(response.data[0]['name'], basestring)
        self.assertIsInstance(response.data[0]['related_artists'], list)
        # Content
        self.assertEqual(response.data[0]['name'], self.artist_kwargs['name'])

    def test_list_artists_as_user_nonempty(self):
        """Get an nonempty list of artists as an unprivileged user"""

        # Create artist
        self.create_artist()

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token)
        response = self.client.get(self.url)

        # Status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Type
        self.assertIsInstance(response.data, list)
        # Content
        self.assertEqual(len(response.data), 1)

        # Type
        self.assertIsInstance(response.data[0], dict)
        # In
        self.assertIn('id', response.data[0])
        self.assertIn('name', response.data[0])
        self.assertIn('related_artists', response.data[0])

        # Type
        self.assertIsInstance(response.data[0]['id'], int)
        self.assertIsInstance(response.data[0]['name'], basestring)
        self.assertIsInstance(response.data[0]['related_artists'], list)
        # Content
        self.assertEqual(response.data[0]['name'], self.artist_kwargs['name'])
        self.assertEqual(response.data[0]['related_artists'], [])

    def test_list_artists_unauthorized(self):
        """Get a list of artists as an unauthenticated user"""

        response = self.client.get(self.url)

        # Status
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RetrieveArtistTestCase(BaseArtistTestCase):

    url = reverse('api_artist_item', kwargs={'pk': 1})

    def test_retrieve_nonexistent_artist_as_admin(self):
        """Retrieve a nonexistent artist as a privileged user"""

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token)
        response = self.client.get(self.url)

        # Status
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_nonexistent_artist_as_user(self):
        """Retrieve a nonexistent artist as an unprivileged user"""

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token)
        response = self.client.get(self.url)

        # Status
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_artist_as_admin(self):
        """Retrieve an artist as a privileged user"""

        # Create artist
        self.create_artist()

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token)
        response = self.client.get(self.url)

        # Status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Type
        self.assertIsInstance(response.data, dict)
        # In
        self.assertIn('id', response.data)
        self.assertIn('name', response.data)
        self.assertIn('related_artists', response.data)

        # Type
        self.assertIsInstance(response.data['id'], int)
        self.assertIsInstance(response.data['name'], basestring)
        self.assertIsInstance(response.data['related_artists'], list)
        # Content
        self.assertEqual(response.data['name'], self.artist_kwargs['name'])
        self.assertEqual(response.data['related_artists'], [])

    def test_retrieve_artist_as_user(self):
        """Retrieve an artist as an unprivileged user"""

        # Create artist
        self.create_artist()

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token)
        response = self.client.get(self.url)

        # Status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Type
        self.assertIsInstance(response.data, dict)
        # In
        self.assertIn('id', response.data)
        self.assertIn('name', response.data)
        self.assertIn('related_artists', response.data)

        # Type
        self.assertIsInstance(response.data['id'], int)
        self.assertIsInstance(response.data['name'], basestring)
        self.assertIsInstance(response.data['related_artists'], list)
        # Content
        self.assertEqual(response.data['name'], self.artist_kwargs['name'])
        self.assertEqual(response.data['related_artists'], [])

    def test_retrieve_nonexistent_artist_unauthorized(self):
        """Retrieve a nonexistent artist as an unauthenticated user"""

        response = self.client.get(self.url)

        # Status
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_artist_unauthorized(self):
        """Retrieve an artist as an unauthenticated user"""

        response = self.client.get(self.url)

        # Status
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UpdateArtistTestCase(BaseArtistTestCase):

    url = reverse('api_artist_item', kwargs={'pk': 1})

    artist_payload = {
        "name": "Cosme Fulanito"
    }

    def test_update_nonexistent_artist_as_admin(self):
        """Update a nonexistent artist as a privileged user"""

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token)
        response = self.client.patch(self.url, data=self.artist_payload, format='json')

        # Status
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_nonexistent_artist_as_user(self):
        """Update a nonexistent artist as an unprivileged user"""

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token)
        response = self.client.patch(self.url, data=self.artist_payload, format='json')

        # Status
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_artist_as_admin(self):
        """Update an artist as a privileged user"""

        # Create artist
        self.create_artist()

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token)
        response = self.client.patch(self.url, data=self.artist_payload, format='json')

        # Status
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Type
        self.assertIsInstance(response.data, dict)
        # In
        self.assertIn('id', response.data)
        self.assertIn('name', response.data)
        self.assertIn('related_artists', response.data)

        # Type
        self.assertIsInstance(response.data['id'], int)
        self.assertIsInstance(response.data['name'], basestring)
        self.assertIsInstance(response.data['related_artists'], list)
        # Content
        self.assertEqual(response.data['name'], self.artist_payload['name'])
        self.assertEqual(response.data['related_artists'], [])

    def test_update_artist_as_user(self):
        """Update an artist as an unprivileged user"""

        # Create artist
        self.create_artist()

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token)
        response = self.client.patch(self.url, data=self.artist_payload, format='json')

        # Status
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_nonexistent_artist_unauthorized(self):
        """Update a nonexistent artist as an unauthenticated user"""
        response = self.client.patch(self.url, data=self.artist_payload, format='json')

        # Status
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_artist_unauthorized(self):
        """Update an artist as an unauthenticated user"""

        # Create artist
        self.create_artist()

        response = self.client.patch(self.url, data=self.artist_payload, format='json')

        # Status
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DestroyArtistTestCase(BaseArtistTestCase):

    url = reverse('api_artist_item', kwargs={'pk': 1})

    def test_destroy_nonexistent_artist_as_admin(self):
        """Destroy a nonexistent artist as a privileged user"""

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token)
        response = self.client.delete(self.url)

        # Status
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_destroy_nonexistent_artist_as_user(self):
        """Destroy a nonexistent artist as an unprivileged user"""

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token)
        response = self.client.delete(self.url)

        # Status
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_destroy_artist_as_admin(self):
        """Destroy an artist as a privileged user"""
        # Create artist
        self.create_artist()

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token)
        response = self.client.delete(self.url)

        # Status
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_destroy_artist_as_user(self):
        """Destroy an artist as an unprivileged user"""

        # Create artist
        self.create_artist()

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token)
        response = self.client.delete(self.url)

        # Status
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_destroy_nonexistent_artist_unauthorized(self):
        """Update a nonexistent artist as an unauthenticated user"""
        response = self.client.delete(self.url)

        # Status
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_destroy_artist_unauthorized(self):
        """Update an artist as an unauthenticated user"""

        # Create artist
        self.create_artist()

        response = self.client.delete(self.url)

        # Status
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CreateAlbumTestCase(APITestCase):

    users_kwargs = {
        'admin': {
            'username': 'admin',
            'password': 'asdasdasd',
            'is_staff': True
        },
        'user': {
            'username': 'user',
            'password': 'qweqweqwe',
            'is_staff': False
        }
    }

    artists_kwargs = [
        {
            'name': "Guns N' Roses"
        },
        {
            'name': "Bob Dylan"
        }
    ]

    album_payload = {
        'artist': None,
        'name': "Use Your Illusion II",
        'release_date': "1991-09-17",
        'cover': None,  # Filled later
        'tracks': [
            {
                'index': 1,
                'name': "Civil War",
                'audio': None   # Filled later
            },
            {
                'index': 4,
                'collaborators': None,  # Filled later
                'name': "Knockin' on Heaven's Door",
                'audio': None   # Filled later
            },
        ]
    }

    def setUp(self):

        # Create users
        admin = User.objects.create_user(**self.users_kwargs['admin'])
        user = User.objects.create_user(**self.users_kwargs['user'])

        # Create artists
        artist_1 = Artist.objects.create(**self.artists_kwargs[0])
        artist_2 = Artist.objects.create(**self.artists_kwargs[1])

        # Load files
        with open("test_files/cover.jpg") as cover:
            cover_b64 = base64.b64encode(cover.read())
        with open("test_files/track.mp3") as track:
            track_b64 = base64.b64encode(track.read())

        # Complete kwargs
        self.album_payload['artist'] = artist_1.id
        self.album_payload['cover'] = cover_b64
        self.album_payload['tracks'][0]['audio'] = track_b64
        self.album_payload['tracks'][1]['collaborators'] = [artist_2.id]
        self.album_payload['tracks'][1]['audio'] = track_b64

        # Shared data
        self.url = reverse('api_album')
        self.admin_token = Token.objects.create(user=admin).key
        self.user_token = Token.objects.create(user=user).key
        self.artist_1 = artist_1
        self.artist_2 = artist_2

    def test_create_album_as_admin(self):
        """Create an album as a privileged user"""
        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token)
        response = self.client.post(self.url, data=self.album_payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Outer object
        self.assertIsInstance(response.data, dict)
        # In
        self.assertIn('id', response.data)
        self.assertIn('artist', response.data)
        self.assertIn('collaborators', response.data)
        self.assertIn('name', response.data)
        self.assertIn('release_date', response.data)
        self.assertIn('cover', response.data)
        self.assertIn('tracks', response.data)
        # Type
        self.assertIsInstance(response.data['id'], int)
        self.assertIsInstance(response.data['artist'], int)
        self.assertIsInstance(response.data['collaborators'], list)
        self.assertIsInstance(response.data['name'], basestring)
        self.assertRegexpMatches(response.data['release_date'], r"\d{4}-\d{2}-\d{2}")
        self.assertRegexpMatches(response.data['cover'], r"http:\/\/testserver\/media\/[a-f0-9]{8}-[a-f0-9]{3}\.(?:jpg|png|gif|bmp)")
        self.assertIsInstance(response.data['tracks'], list)
        # Content
        self.assertEqual(response.data['name'], self.album_payload['name'])
        self.assertEqual(response.data['artist'], self.artist_1.id)
        self.assertItemsEqual(response.data['collaborators'], self.album_payload['tracks'][1]['collaborators'])
        self.assertEqual(response.data['release_date'], self.album_payload['release_date'])

        # Tracks
        self.assertEqual(len(response.data['tracks']), 2)
        # Type
        self.assertIsInstance(response.data['tracks'][0], dict)
        self.assertIsInstance(response.data['tracks'][1], dict)

        # Track 0
        # In
        self.assertIn('id', response.data['tracks'][0])
        self.assertIn('index', response.data['tracks'][0])
        self.assertIn('collaborators', response.data['tracks'][0])
        self.assertIn('name', response.data['tracks'][0])
        self.assertIn('audio', response.data['tracks'][0])
        # Type
        self.assertIsInstance(response.data['tracks'][0]['id'], int)
        self.assertIsInstance(response.data['tracks'][0]['index'], int)
        self.assertIsInstance(response.data['tracks'][0]['collaborators'], list)
        self.assertRegexpMatches(response.data['tracks'][0]['audio'], r"http:\/\/testserver\/media\/[a-f0-9]{8}-[a-f0-9]{3}\.mp3")
        # Content
        self.assertEqual(response.data['tracks'][0]['index'], 1)
        self.assertEqual(response.data['tracks'][0]['collaborators'], [])
        self.assertEqual(response.data['tracks'][0]['name'], self.album_payload['tracks'][0]['name'])

        # Track 1
        # In
        self.assertIn('id', response.data['tracks'][1])
        self.assertIn('index', response.data['tracks'][1])
        self.assertIn('collaborators', response.data['tracks'][1])
        self.assertIn('name', response.data['tracks'][1])
        self.assertIn('audio', response.data['tracks'][1])
        # Type
        self.assertIsInstance(response.data['tracks'][1]['id'], int)
        self.assertIsInstance(response.data['tracks'][1]['index'], int)
        self.assertIsInstance(response.data['tracks'][1]['collaborators'], list)
        self.assertRegexpMatches(response.data['tracks'][1]['audio'], r"http:\/\/testserver\/media\/[a-f0-9]{8}-[a-f0-9]{3}\.mp3")
        # Content
        self.assertEqual(response.data['tracks'][1]['index'], 4)
        self.assertItemsEqual(response.data['tracks'][1]['collaborators'], self.album_payload['tracks'][1]['collaborators'])
        self.assertEqual(response.data['tracks'][1]['name'], self.album_payload['tracks'][1]['name'])

    def test_create_album_as_user(self):
        """Create an album as an unprivileged user"""
        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token)
        response = self.client.post(self.url, data=self.album_payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_album_unauthorized(self):
        """Create an album as an unauthenticated user"""
        response = self.client.post(self.url, data=self.album_payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BaseAlbumTestCase(APITestCase):
    """A test class for tests which need a created album"""

    users_kwargs = {
        'admin': {
            'username': 'admin',
            'password': 'asdasdasd',
            'is_staff': True
        },
        'user': {
            'username': 'user',
            'password': 'qweqweqwe',
            'is_staff': False
        }
    }

    artists_kwargs = [
        {
            'name': "Guns N' Roses"
        },
        {
            'name': "Bob Dylan"
        }
    ]

    album_1_kwargs = {
        'artist': None, # Filled later
        'name': "Use Your Illusion II",
        'release_date': parse_ISO8601("1991-09-17"),
        'cover': None,  # Filled later
    }

    album_2_kwargs = {
        'artist': None, # Filled later
        'name': "Use Your Illusion III",
        'release_date': parse_ISO8601("2050-01-01"),
        'cover': None, # Filled later
    }

    tracks_1_kwargs = [
        {
            'artist': None, # Filled later
            'album': None,  # Filled later
            'index': 1,
            'name': "Civil War",
            'audio': None   # Filled later
        },
        {
            'artist': None, # Filled later
            'album': None,  # Filled later
            'index': 4,
            'name': "Knockin' on Heaven's Door",
            'audio': None   # Filled later
        },
    ]

    tracks_2_kwargs = [
        {
            'artist': None,  # Filled later
            'album': None,  # Filled later
            'index': 1,
            'name': "Civil Love",
            'audio': None  # Filled later
        },
        {
            'artist': None,  # Filled later
            'album': None,  # Filled later
            'index': 4,
            'name': "Knockin' on Hell's Door",
            'audio': None  # Filled later
        },
    ]

    def setUp(self):
        # Create users
        admin = User.objects.create_user(**self.users_kwargs['admin'])
        user = User.objects.create_user(**self.users_kwargs['user'])

        # Create artists
        artist_1 = Artist.objects.create(**self.artists_kwargs[0])
        artist_2 = Artist.objects.create(**self.artists_kwargs[1])

        # Load files
        with open("test_files/cover.jpg") as cover:
            cover_b64 = base64.b64encode(cover.read())
        with open("test_files/track.mp3") as track:
            track_b64 = base64.b64encode(track.read())

        # Complete album kwargs
        self.album_1_kwargs['artist'] = artist_1
        self.album_1_kwargs['cover'] = cover_b64
        self.album_2_kwargs['artist'] = artist_1
        self.album_2_kwargs['cover'] = cover_b64

        # Shared data
        self.admin = admin
        self.user = user

        self.admin_token = Token.objects.create(user=admin).key
        self.user_token = Token.objects.create(user=user).key

        self.artist_1 = artist_1
        self.artist_2 = artist_2

        self.cover_b64 = cover_b64
        self.track_b64 = track_b64

    def create_album_1(self):

        # Create album
        album_1 = Album.objects.create(**self.album_1_kwargs)

        # Complete tracks kwargs
        self.tracks_1_kwargs[0]['artist'] = self.artist_1
        self.tracks_1_kwargs[0]['album'] = album_1
        self.tracks_1_kwargs[0]['audio'] = self.track_b64

        self.tracks_1_kwargs[1]['artist'] = self.artist_1
        self.tracks_1_kwargs[1]['album'] = album_1
        self.tracks_1_kwargs[1]['audio'] = self.track_b64

        # Create tracks
        track_1 = Track.objects.create(**self.tracks_1_kwargs[0])
        track_2 = Track.objects.create(**self.tracks_1_kwargs[1])

        # Add collaborator
        track_2.collaborators.add(self.artist_2)

        # Shared data
        self.album_1 = album_1

        self.track_1 = track_1
        self.track_2 = track_2

    def create_album_2(self):

        # Create album
        album_2 = Album.objects.create(**self.album_2_kwargs)

        # Complete tracks kwargs
        self.tracks_2_kwargs[0]['artist'] = self.artist_1
        self.tracks_2_kwargs[0]['album'] = album_2
        self.tracks_2_kwargs[0]['audio'] = self.track_b64

        self.tracks_2_kwargs[1]['artist'] = self.artist_1
        self.tracks_2_kwargs[1]['album'] = album_2
        self.tracks_2_kwargs[1]['audio'] = self.track_b64

        # Create tracks
        track_3 = Track.objects.create(**self.tracks_2_kwargs[0])
        track_4 = Track.objects.create(**self.tracks_2_kwargs[1])

        # Add collaborator
        track_4.collaborators.add(self.artist_2)

        # Shared data
        self.album_2 = album_2

        self.track_3 = track_3
        self.track_4 = track_4

    def create_albums(self):

        self.create_album_1()
        self.create_album_2()


class ListAlbumTestCase(BaseAlbumTestCase):

    url = reverse('api_album')

    def test_list_albums_as_admin_empty(self):
        """Get an empty list of albums as a privileged user"""

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token)
        response = self.client.get(self.url)

        # Status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Type
        self.assertIsInstance(response.data, list)
        # Content
        self.assertEqual(response.data, [])

    def test_list_albums_as_user_empty(self):
        """Get an empty list of albums as an unprivileged user"""

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token)
        response = self.client.get(self.url)

        # Status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Type
        self.assertIsInstance(response.data, list)
        # Content
        self.assertEqual(response.data, [])

    def test_list_albums_as_admin_nonempty(self):
        """Get an nonempty list of albums as a privileged user"""

        # Create albums
        self.create_albums()

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token)
        response = self.client.get(self.url)

        # Status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Type
        self.assertIsInstance(response.data, list)
        # Content
        self.assertEqual(len(response.data), 2)

        # TODO Test response content

    def test_list_albums_as_user_nonempty(self):
        """Get an nonempty list of albums as an unprivileged user"""

        # Create albums
        self.create_albums()

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token)
        response = self.client.get(self.url)

        # Status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Type
        self.assertIsInstance(response.data, list)
        # Content
        self.assertEqual(len(response.data), 1)

        # TODO Test response content


    def test_list_albums_unauthorized(self):
        """Get a list of albums as an unauthenticated user"""

        response = self.client.get(self.url)

        # Status
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ListArtistAlbumTestCase(BaseAlbumTestCase):

    url = reverse('api_artist_item_album', kwargs={ 'artist_id': 1 })
    url_404 = reverse('api_artist_item_album', kwargs={ 'artist_id': 10 })

    def test_list_nonexistent_artist_albums_as_admin(self):
        """Get a list of albums of a nonexistent artist as a privileged user"""

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token)
        response = self.client.get(self.url_404)

        # Status
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_nonexistent_artist_albums_as_user(self):
        """Get a list of albums of a nonexistent artist as an unprivileged user"""

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token)
        response = self.client.get(self.url_404)

        # Status
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_artist_albums_as_admin_empty(self):
        """Get a list of albums of an artist with no albums as a privileged user"""

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token)
        response = self.client.get(self.url)

        # Status
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Type
        self.assertIsInstance(response.data, list)
        # Content
        self.assertEqual(response.data, [])

        # TODO Test response content

    def test_list_artist_albums_as_user_empty(self):
        """Get a list of albums of an artist with no albums as an unprivileged user"""

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token)
        response = self.client.get(self.url)

        # Status
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Type
        self.assertIsInstance(response.data, list)
        # Content
        self.assertEqual(response.data, [])

        # TODO Test response content

    def test_list_artist_albums_as_admin_nonempty(self):
        """Get an nonempty list of albums as a privileged user"""

        # Create albums
        self.create_albums()

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token)
        response = self.client.get(self.url)

        # Status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Type
        self.assertIsInstance(response.data, list)
        # Content
        self.assertEqual(len(response.data), 2)

        # TODO Test response content

    def test_list_artist_albums_as_user_nonempty(self):
        """Get an nonempty list of albums as an unprivileged user"""

        # Create albums
        self.create_albums()

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token)
        response = self.client.get(self.url)

        # Status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Type
        self.assertIsInstance(response.data, list)
        # Content
        self.assertEqual(len(response.data), 1)

        # TODO Test response content


class RetrieveAlbumTestCase(BaseAlbumTestCase):

    url_1 = reverse('api_album_item', kwargs={'pk': 1})
    url_2 = reverse('api_album_item', kwargs={'pk': 2})

    def test_retrieve_nonexistent_album_as_admin(self):
        """Retrieve a nonexistent album as a privileged user"""

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token)
        response = self.client.get(self.url_1)

        # Status
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_nonexistent_album_as_user(self):
        """Retrieve a nonexistent album as an unprivileged user"""

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token)
        response = self.client.get(self.url_1)

        # Status
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_album_as_admin(self):
        """Retrieve an album as a privileged user"""

        # Create albums
        self.create_albums()

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token)
        response = self.client.get(self.url_1)

        # Status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Type
        self.assertIsInstance(response.data, dict)

        # TODO Test response content

    def test_retrieve_album_as_user(self):
        """Retrieve an album as an unprivileged user"""

        # Create albums
        self.create_albums()

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token)
        response = self.client.get(self.url_1)

        # Status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Type
        self.assertIsInstance(response.data, dict)

        # TODO Test response content

    def test_retrieve_tbd_album_as_admin(self):
        """Retrieve a TBD album as a privileged user"""

        # Create albums
        self.create_albums()

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token)
        response = self.client.get(self.url_2)

        # Status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Type
        self.assertIsInstance(response.data, dict)

        # TODO Test response content

    def test_retrieve_tbd_album_as_user(self):
        """Retrieve a TBD album as an unprivileged user"""

        # Create albums
        self.create_albums()

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token)
        response = self.client.get(self.url_2)

        # Status
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_nonexistent_album_unauthorized(self):
        """Retrieve a nonexistent album as an unauthenticated user"""

        # Authenticate
        response = self.client.get(self.url_1)

        # Status
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_album_unauthorized(self):
        """Retrieve an album as an unauthenticated user"""

        # Create albums
        self.create_albums()

        # Authenticate
        response = self.client.get(self.url_1)

        # Status
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UpdateAlbumTestCase(BaseAlbumTestCase):

    url_1 = reverse('api_album_item', kwargs={'pk': 1})
    url_2 = reverse('api_album_item', kwargs={'pk': 2})

    # TODO More complete update payload
    album_payload = {
        'name': "Master of Puppets"
    }

    def test_update_nonexistent_album_as_admin(self):
        """Update a nonexistent album as a privileged user"""

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token)
        response = self.client.patch(self.url_1, data=self.album_payload, format='json')

        # Status
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_nonexistent_album_as_user(self):
        """Update a nonexistent album as an unprivileged user"""

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token)
        response = self.client.patch(self.url_1, data=self.album_payload, format='json')

        # Status
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_album_as_admin(self):
        """Update an album as a privileged user"""

        # Create albums
        self.create_albums()

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token)
        response = self.client.patch(self.url_1, data=self.album_payload, format='json')

        # Status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # TODO Test response content

    def test_update_album_as_user(self):
        """Update an album as an unprivileged user"""

        # Create albums
        self.create_albums()

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token)
        response = self.client.patch(self.url_1, data=self.album_payload, format='json')

        # Status
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_tbd_album_as_admin(self):
        """Update a TBD album as a privileged user"""

        # Create albums
        self.create_albums()

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token)
        response = self.client.patch(self.url_2, data=self.album_payload, format='json')

        # Status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # TODO Test response content

    def test_update_tbd_album_as_user(self):
        """Update a TBD album as an unprivileged user"""

        # Create albums
        self.create_albums()

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token)
        response = self.client.patch(self.url_2, data=self.album_payload, format='json')

        # Status
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_nonexistent_album_unauthorized(self):
        """Update a nonexistent album as an unauthenticated user"""

        response = self.client.patch(self.url_1, data=self.album_payload, format='json')

        # Status
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_album_unauthorized(self):
        """Update an album as an unauthenticated user"""

        # Create albums
        self.create_albums()

        response = self.client.patch(self.url_1, data=self.album_payload, format='json')

        # Status
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DestroyAlbumTestCase(BaseAlbumTestCase):

    url_1 = reverse('api_album_item', kwargs={'pk': 1})
    url_2 = reverse('api_album_item', kwargs={'pk': 2})

    def test_destroy_nonexistent_album_as_admin(self):
        """Destroy a nonexistent album as a privileged user"""

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token)
        response = self.client.delete(self.url_1)

        # Status
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_destroy_nonexistent_album_as_user(self):
        """Destroy a nonexistent album as an unprivileged user"""

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token)
        response = self.client.delete(self.url_1)

        # Status
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_destroy_album_as_admin(self):
        """Destroy an album as a privileged user"""

        # Create albums
        self.create_albums()

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token)
        response = self.client.delete(self.url_1)

        # Status
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


    def test_destroy_tbd_album_as_admin(self):
        """Destroy a TBD album as a privileged user"""

        # Create albums
        self.create_albums()

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token)
        response = self.client.delete(self.url_2)

        # Status
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


    def test_destroy_album_as_user(self):
        """Destroy an album as an unprivileged user"""

        # Create albums
        self.create_albums()

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token)
        response = self.client.delete(self.url_1)

        # Status
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_destroy_tbd_album_as_user(self):
        """Destroy a TBD album as an unprivileged user"""

        # Create albums
        self.create_albums()

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token)
        response = self.client.delete(self.url_2)

        # Status
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_destroy_nonexistent_album_unauthorized(self):
        """Destroy a nonexistent album as an unauthenticated user"""

        response = self.client.delete(self.url_1)

        # Status
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_destroy_album_unauthorized(self):
        """Destroy an album as an unauthenticated user"""

        # Create albums
        self.create_albums()

        response = self.client.delete(self.url_1)

        # Status
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RetrieveTrackTestCase(BaseAlbumTestCase):

    url_1 = reverse('api_track_item', kwargs={'pk': 1})
    url_3 = reverse('api_track_item', kwargs={'pk': 3})

    def test_retrieve_nonexistent_track_as_admin(self):
        """Retrieve a nonexistent track as a privileged user"""

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token)
        response = self.client.get(self.url_1)

        # Status
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_nonexistent_track_as_user(self):
        """Retrieve a nonexistent track as an unprivileged user"""

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token)
        response = self.client.get(self.url_1)

        # Status
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_track_as_admin(self):
        """Retrieve a track as a privileged user"""

        # Create albums
        self.create_albums()

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token)
        response = self.client.get(self.url_1)

        # Status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # TODO Test response content

    def test_retrieve_track_as_user(self):
        """Retrieve a track as an unprivileged user"""

        # Create albums
        self.create_albums()

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token)
        response = self.client.get(self.url_1)

        # Status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # TODO Test response content

    def test_retrieve_tbd_track_as_admin(self):
        """Retrieve a TBD track as a privileged user"""

        # Create albums
        self.create_albums()

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token)
        response = self.client.get(self.url_3)

        # Status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # TODO Test response content

    def test_retrieve_tbd_track_as_user(self):
        """Retrieve a TBD track as an unprivileged user"""

        # Create albums
        self.create_albums()

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token)
        response = self.client.get(self.url_3)

        # Status
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_nonexistent_track_unauthorized(self):
        """Retrieve a nonexistent track as an unauthenticated user"""

        # Authenticate
        response = self.client.get(self.url_1)

        # Status
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_track_unauthorized(self):
        """Retrieve a track as an unauthenticated user"""

        # Create albums
        self.create_albums()

        # Authenticate
        response = self.client.get(self.url_1)

        # Status
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UpdateTrackTestCase(BaseAlbumTestCase):

    url_1 = reverse('api_track_item', kwargs={'pk': 1})
    url_3 = reverse('api_track_item', kwargs={'pk': 3})

    # TODO More complete update payload
    track_payload = {
        'name': "Maste of Puppets"
    }

    def test_update_nonexistent_track_as_admin(self):
        """Update a nonexistent track as a privileged user"""

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token)
        response = self.client.patch(self.url_1, data=self.track_payload, format='json')

        # Status
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_nonexistent_track_as_user(self):
        """Update a nonexistent track as an unprivileged user"""

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token)
        response = self.client.patch(self.url_1, data=self.track_payload, format='json')

        # Status
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_track_as_admin(self):
        """Update a track as a privileged user"""

        # Create albums
        self.create_albums()

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token)
        response = self.client.patch(self.url_1, data=self.track_payload, format='json')

        # Status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # TODO Test response content

    def test_update_track_as_user(self):
        """Update a track as an unprivileged user"""

        # Create albums
        self.create_albums()

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token)
        response = self.client.patch(self.url_1, data=self.track_payload, format='json')

        # Status
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_tbd_track_as_admin(self):
        """Update a TBD track as a privileged user"""

        # Create albums
        self.create_albums()

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token)
        response = self.client.patch(self.url_3, data=self.track_payload, format='json')

        # Status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # TODO Test response content

    def test_update_tbd_track_as_user(self):
        """Update a TBD track as an unprivileged user"""

        # Create albums
        self.create_albums()

        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token)
        response = self.client.patch(self.url_3, data=self.track_payload, format='json')

        # Status
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_nonexistent_track_unauthorized(self):
        """Update a nonexistent track as an unauthenticated user"""

        # Authenticate
        response = self.client.patch(self.url_1, data=self.track_payload, format='json')

        # Status
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_track_unauthorized(self):
        """Update a track as an unauthenticated user"""

        # Create albums
        self.create_albums()

        # Authenticate
        response = self.client.patch(self.url_1, data=self.track_payload, format='json')

        # Status
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
