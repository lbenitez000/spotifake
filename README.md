# Spotifake

Spotifake es un proyecto de ejemplo que usa Django y [Django REST Framework](https://github.com/encode/django-rest-framework/).

La aplicación funciona como una versión simplificada de Spotify. Permite crear Artistas y Álbumes con pistas.

## API
Se adjunta una colección de Postman en el archivo `spotifake.postman_collection.json`.

## Modelo de datos
Existen tres modelos: Artist, Album y Track. Cada Album pertenece a un Artist. Cada Track pertenece a un Album y un Artist y además puede tener otros Artist como colaboradores.

## Serializers
Se usan ModelSerializer para cada modelo. En `serializers.py` Hay ejemplos de custom fields, campos dinámicos, campos anidados, y creación de objetos con campos anidados.

## Views
Se usan Generic Views con algunas implementaciones personalizadas de `get_queryset` para filtrar los resultados de Album y Track según el tipo de usuario y la fecha de publicación del Album.

## Permissions
En `permissions.py` hay una implementación de IsAdminOrReadOnly, que permite operaciones de escritura solo a usuarios administradores.

## Renderers
Como una solución a la vulnerabilidad descrita en [http://haacked.com/archive/2008/11/20/anatomy-of-a-subtle-json-vulnerability.aspx/](http://haacked.com/archive/2008/11/20/anatomy-of-a-subtle-json-vulnerability.aspx/), se usa un Renderer personalizado que envuelve en un diccionario todas las respuestas que tienen como raíz una lista. El nombre del objeto envolvente se define en el serializer.

## Base de datos
Se incluye una base de datos sqlite3 pre-cargada con el usuario administrador `admin` (password `asdasdasd`), dos artistas, un álbum y dos canciones.