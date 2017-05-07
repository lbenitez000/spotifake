from django.contrib.gis.geos import Point, Polygon
from rest_framework import serializers
from drf_extra_fields.fields import Base64FileField


class AudioField(Base64FileField):

    ALLOWED_TYPES = ['mp3']

    def get_file_extension(self, filename, decoded_file):
        return 'mp3'


class PointField(serializers.Field):

    def to_representation(self, obj):
        return {
            'lng': obj.coords[0],
            'lat': obj.coords[1],
        } if obj else None

    def to_internal_value(self, data):
        if data is None:
            return None

        if not isinstance(data, dict) or not 'lng' in data or not 'lat' in data:
            raise serializers.ValidationError("Invalid coordinates. Must be a lat-lng object.")

        if not isinstance(data['lng'], (int, float)) or not isinstance(data['lat'], (int, float)):
            raise serializers.ValidationError("Invalid coordinates. Longitude and latitude must have numeric values")

        lat = data['lat']
        lng = data['lng']
        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            raise serializers.ValidationError("Invalid coordinates. Coordinates out of bounds.")

        try:
            point = Point(lng, lat)
        except:
            raise serializers.ValidationError("Invalid coordinates")

        return point


# TODO Support multi-ring polygons
class PolygonField(serializers.Field):

    def to_representation(self, obj):
        return [
            {
                'lng': vertex[0],
                'lat': vertex[1],
            }
        for vertex in obj.coords[0]] if obj else None

    def to_internal_value(self, data):
        if data is None:
            return None

        if not isinstance(data, list):
            raise serializers.ValidationError("Invalid coordinates. Must be a list of lat-lng objects.")

        for vertex in data:
            if not isinstance(vertex, dict) or not 'lng' in vertex or not 'lat' in vertex:
                raise serializers.ValidationError("Invalid coordinates. Must be a list of lat-lng objects.")
            if not isinstance(vertex['lng'], (int, float)) or not isinstance(vertex['lat'], (int, float)):
                raise serializers.ValidationError("Invalid coordinates. Longitude and latitude must have numeric values")

            lat = vertex['lat']
            lng = vertex['lng']
            if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
                raise serializers.ValidationError("Invalid coordinates. Coordinates out of bounds.")

        if len(data) < 4:
            raise serializers.ValidationError("Invalid coordinates. Must have at least 4 points.")

        if data[0] != data[-1]:
            raise serializers.ValidationError("Invalid coordinates. First and last points must be equal.")

        vertexes = []
        for vertex in data:
            lat = vertex['lat']
            lng = vertex['lng']

            vertexes.append((lng, lat))

        try:
            polygon = Polygon(vertexes)
        except:
            raise serializers.ValidationError("Invalid coordinates")

        return polygon