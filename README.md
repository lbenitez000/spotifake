# Spotifake (Spanish)

Spotifake es un proyecto de ejemplo que usa Django y [Django REST Framework](https://github.com/encode/django-rest-framework/).

La aplicación funciona como una versión simplificada de Spotify. Permite crear artistas y álbumes con pistas. Hay una explicación en el siguiente video.

[https://youtu.be/tn23rDtb_q0](https://youtu.be/tn23rDtb_q0)

## API
Se adjunta una colección de [Postman](https://www.getpostman.com/) en el archivo [spotifake.postman_collection.json](spotifake.postman_collection.json).

## Modelo de datos
Existen tres modelos: Artist, Album y Track. Cada Album pertenece a un Artist. Cada Track pertenece a un Album y un Artist y además puede tener otros Artist como colaboradores.

## Serializers
Se usan ModelSerializer para cada modelo. En [serializers.py](music/serializers.py) hay ejemplos de custom fields, campos dinámicos, campos anidados y creación de objetos con campos anidados.

## Views
Se usan Generic Views con algunas implementaciones personalizadas de `get_queryset` para filtrar los resultados de Album y Track según el tipo de usuario y la fecha de publicación del Album.

## Permissions
En [permissions.py](spotifake/permissions.py) hay una implementación de IsAdminOrReadOnly, que permite operaciones de escritura solo a usuarios administradores.

## Renderers
Como una solución a la vulnerabilidad descrita en [http://haacked.com/archive/2008/11/20/anatomy-of-a-subtle-json-vulnerability.aspx/](http://haacked.com/archive/2008/11/20/anatomy-of-a-subtle-json-vulnerability.aspx/), se usa un Renderer personalizado que envuelve en un diccionario todas las respuestas que tienen como raíz una lista. El nombre de la llave que contiene la lista se define en el serializer.

## Base de datos
Se incluye una base de datos sqlite3 pre-cargada con el usuario administrador `admin` (password `asdasdasd`), dos artistas, un álbum y dos pistas.

# Spotifake (English)
Spotifake is a sample project made with Django and [Django REST Framework](https://github.com/encode/django-rest-framework/).

The app works as a very simplified version of Spotify. It allows to create artists, albums and tracks.

## API
There is a [Postman](https://www.getpostman.com/) collection with the API specs in [spotifake.postman_collection.json](spotifake.postman_collection.json).

## Data Model
There are three models: Artist, Album and Track. Each Album belongs to an Artist. Each Track belongs to an Album and and Artist. Tracks can also have other Artists as collaborators.

## Serializers
There is a ModelSerializer for each model. In [serializers.py](music/serializers.py) there are uses of custom fields, dynamic fields, nested fields and creation of objects with nested fields.

## Views
There are some Generic Views with customized implementations of `get_queryset` to filter results by Album and Track depending on the user privileges and the release date of the album.

## Permissions
In [permissions.py](spotifake/permissions.py) there is an implementation of `IsAdminOrReadOnly`, which allows write operations only to administrators.

## Renderers
To prevent attacks as described in [http://haacked.com/archive/2008/11/20/anatomy-of-a-subtle-json-vulnerability.aspx/](http://haacked.com/archive/2008/11/20/anatomy-of-a-subtle-json-vulnerability.aspx/), a custom Renderer is used. It wraps every array response in a dictionary. The name of the key that will contain the array is defined in the serializer.

## Database
A preloaded sqlite3 database is included. It contains the admin user (U:`admin`, P:`asdasdasd`), two artists, one album and two tracks.
