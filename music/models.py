# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Artist(models.Model):

    name = models.CharField(max_length=256)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Album(models.Model):

    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='albums')

    name = models.CharField(max_length=256)
    release_date = models.DateField()
    cover = models.ImageField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Track(models.Model):

    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='tracks')
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='tracks')
    collaborators = models.ManyToManyField(Artist, related_name='collaborations')

    index = models.PositiveIntegerField()
    name = models.CharField(max_length=256)
    audio = models.FileField()
