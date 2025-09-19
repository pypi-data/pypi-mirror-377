from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from wagtail.admin.forms import WagtailAdminPageForm


class SoundType(models.TextChoices):
    FILE = "file", _("File")
    URL = "url", _("External URL")

    __empty__ = "---------"


class RadioShowPageForm(WagtailAdminPageForm):
    title = forms.CharField(label=_("Title"))


class PodcastPageForm(WagtailAdminPageForm):
    """
    Form used for creating and editing a Podcast page in the admin.

    The `sound_external_url` value or the `sound_file` will be validated on
    client side by trying to load it as an Audio object. This will trigger the
    `is_sound_valid` field and set the `duration` field if the audio could be
    loaded.
    """

    title = forms.CharField(label=_("Title"))

    sound_type = forms.ChoiceField(
        choices=SoundType.choices,
        label=_("Type"),
        widget=forms.Select(
            attrs={
                "data-action": "podcast-sound#setType",
                "data-podcast-sound-target": "type",
            },
        ),
    )
    is_sound_valid = forms.BooleanField(
        initial=False,
        required=False,
        widget=forms.HiddenInput(),
    )

    class Media:
        js = ("wagtail_webradio/admin/js/podcast-form.js",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not getattr(settings, "WEBRADIO_PODCAST_SOUND_FILE", True):
            del self.fields["sound_file"]
            del self.fields["sound_type"]
        elif self.instance.pk:
            if self.instance.sound_file:
                self.initial["sound_type"] = SoundType.FILE
            elif self.instance.sound_external_url:
                self.initial["sound_type"] = SoundType.URL

    def clean(self):
        cleaned_data = super().clean()

        if not self.has_error("sound_type"):
            sound_type = (
                cleaned_data["sound_type"]
                if "sound_type" in self.fields
                else SoundType.URL
            )

            if sound_type == SoundType.FILE:
                if not cleaned_data["sound_file"]:
                    self.add_error(
                        "sound_file",
                        ValidationError(
                            self.fields["sound_file"].error_messages[
                                "required"
                            ],
                            code="required",
                        ),
                    )
                else:
                    # Reset value and errors of the sound URL field
                    cleaned_data["sound_external_url"] = ""
                    self._errors.pop("sound_external_url", None)

            elif sound_type == SoundType.URL:
                if not cleaned_data["sound_external_url"]:
                    self.add_error(
                        "sound_external_url",
                        ValidationError(
                            self.fields["sound_external_url"].error_messages[
                                "required"
                            ],
                            code="required",
                        ),
                    )
                elif "sound_file" in cleaned_data:
                    # Delete the sound file and reset its field errors
                    cleaned_data["sound_file"] = False
                    self._errors.pop("sound_file", None)

        return cleaned_data

    def _post_clean(self):
        super()._post_clean()

        if (
            not self.cleaned_data["is_sound_valid"]
            and not self.has_error("sound_type")
            and not self.has_error("sound_file")
            and not self.has_error("sound_external_url")
        ):
            sound_type = (
                self.cleaned_data["sound_type"]
                if "sound_type" in self.fields
                else SoundType.URL
            )

            if sound_type == SoundType.FILE:
                if "sound_file" in self.changed_data:
                    self.add_error(
                        "sound_file",
                        ValidationError(
                            _(
                                "Unable to retrieve the duration of this file. "
                                "Check that it is a valid audio file."
                            ),
                            code="missing_validation",
                        ),
                    )

            if sound_type == SoundType.URL:
                if "sound_external_url" in self.changed_data:
                    self.add_error(
                        "sound_external_url",
                        ValidationError(
                            _(
                                "Unable to validate the file at this URL. "
                                "Check that it is a valid audio file by "
                                "opening it in a new tab."
                            ),
                            code="missing_validation",
                        ),
                    )
