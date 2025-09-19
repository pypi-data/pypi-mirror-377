from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

import filetype

DEFAULT_ALLOWED_AUDIO_MIME_TYPES = [
    "audio/ogg",
    "audio/mpeg",
    "audio/flac",
    "audio/opus",
]


def validate_audio_file_type(value):
    allowed_types = getattr(
        settings,
        "WEBRADIO_ALLOWED_AUDIO_MIME_TYPES",
        DEFAULT_ALLOWED_AUDIO_MIME_TYPES,
    )

    kind = filetype.guess(value)

    if not kind or kind.mime not in allowed_types:
        raise ValidationError(
            _(
                "File type “%(mimetype)s” is not allowed. Allowed file types "
                "are: %(allowed_mimetypes)s."
                % {
                    "mimetype": kind.mime if kind else _("unknown"),
                    "allowed_mimetypes": ", ".join(allowed_types),
                }
            ),
            code="invalid_mimetype",
        )
