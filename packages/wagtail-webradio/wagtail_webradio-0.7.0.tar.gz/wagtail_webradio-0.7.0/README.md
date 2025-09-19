# wagtail-webradio

Manage your web radio - e.g. podcasts, programs - in Wagtail.

**Warning!** This project is still early on in its development lifecycle. It is
possible for breaking changes to occur between versions until reaching a stable
1.0. Feedback and pull requests are welcome.

## Requirements

This package requires the following:
- **Python 3** (3.10, 3.11, 3.12, 3.13)
- **Django** (4.2 LTS, 5.2 LTS)
- **Wagtail** (7.0 LTS, 7.1)

## Installation

1. Install using ``pip``:
   ```shell
   pip install wagtail-webradio
   ```
2. Add ``wagtail_webradio`` to your ``INSTALLED_APPS`` setting:
   ```python
   INSTALLED_APPS = [
       # ...
       'wagtail_webradio',
       # ...
   ]
   ```
3. Run ``python manage.py migrate`` to create the models

## Usage
### Configuration
#### `WEBRADIO_PODCAST_SOUND_FILE`

Default: ``True``

When set to ``False``, the sound file field of a podcast is disabled and it is
only possible to set the sound by its URL.


#### `WEBRADIO_ALLOWED_AUDIO_MIME_TYPES`

Default:
```python
['audio/ogg', 'audio/mpeg', 'audio/flac', 'audio/opus']
```

A list of audio MIME types which are allowed when uploading a podcast's sound file.

### Frontend components

A player with a playlist management is provided to be easily included into your
frontend. Under the hood, it uses [django-unicorn] with a bit of JavaScript to
manipulate the audio from the Web browser. It is currently unstyled but you can
find an [example][1] when using Bootstrap. You should also have a look to the
[template][2] of this component to know how to extend it.

To make use of it:

1. Install the ``player`` extra of this package:
   ```shell
   pip install wagtail-webradio[player]
   ```
2. Integrate ``Unicorn`` in your project by [following the documentation][3]
3. Configure ``Unicorn`` settings to look for this package's components:
   ```python
   UNICORN = {
       'APPS': ['wagtail_webradio'],
   }
   ```

Then, e.g. in ``base.html``, load the player scripts in the ``<head>`` of your
document and the component in the ``<body>``:
```django
<html>
  <head>
    <!-- […] -->

    <script src="{% static "wagtail_webradio/player/js/main.js" %}" defer></script>
  </head>
  <body>
    <! -- […] -->

    {% unicorn "player" %}

    <! -- […] -->
  </body>
</html>
```

In the case of multi-process production environment, you must switch to redis,
memcache or database caching to make Unicorn working correctly. For example with
memcache listening through unix socket, you can add in settings.py :
```
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
        'LOCATION': 'unix:/var/run/memcached/memcached.sock',
    }
}
```

When the player scripts are loaded, you can simply add a song to the playlist
by defining a ``data-player-add-podcast`` or ``data-player-add`` attribute on an
element, and optionally ``data-player-autoplay`` to play the song once added:
```html
<button data-player-add-podcast="10" data-player-autoplay>Add a podcast by id</button>

<button data-player-add="{'title': 'Title', 'subtitle': 'Subtitle', 'url': 'http://example.org/song.ogg', 'thumbnail_url': 'http://example.org/thumb.png'}">
  Add a song
</button>
```

[1]: examples/player/styles.scss
[2]: wagtail_webradio/templates/wagtail_webradio/components/player.html
[3]: https://www.django-unicorn.com/docs/installation/#integrate-unicorn-with-django
[django-unicorn]: https://www.django-unicorn.com/

## Development
### Quick start

To set up a development environment, ensure that Python 3 is installed on your
system. Then:

1. Clone this repository
2. Create a virtual environment and activate it:
   ```shell
   $ python3 -m venv venv
   $ source venv/bin/activate
   ```
3. Install this package and its requirements:
   ```shell
   (venv)$ pip install --editable ".[components]" --group dev
   ```

To run the test app interactively, use ``tox -e interactive``, visit
[http://127.0.0.1:8020/admin](http://127.0.0.1:8000/admin/) and log in
with `admin` / `changeme`.

### Contributing

The tests are written with [pytest] and code coverage is measured with [coverage].
You can use the following commands while developing:
- ``make test``: run the tests and output a quick report of code coverage
- ``make test-wip``: only run the tests marked as 'wip'
- ``make test-all``: run the tests on all supported versions of Django and
  Wagtail with [tox]

The Python code is formatted and linted thanks to [ruff]. You can check the code
with ``make lint`` and try to fix the reported issues with ``make format``.

When submitting a pull-request, please ensure that the code is well formatted
and covered, and that all the tests pass.

[pytest]: https://docs.pytest.org/
[coverage]: https://coverage.readthedocs.io/
[tox]: https://tox.wiki/
[ruff]: https://docs.astral.sh/ruff/

## License

This extension is mainly developed by [Cliss XXI](https://www.cliss21.com) and
licensed under the [AGPLv3+](LICENSE). Any contribution is welcome!
