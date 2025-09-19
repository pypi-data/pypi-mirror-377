from django import forms
from django.utils.translation import gettext_lazy as _

from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    MultiFieldPanel,
    TitleFieldPanel,
)

from .forms import PodcastPageForm, RadioShowPageForm
from .models import PodcastPage, RadioShowPage
from .widgets import AdminClearableFileInput

RadioShowPage.base_form_class = RadioShowPageForm
RadioShowPage.content_panels = [
    TitleFieldPanel(
        "title",
        placeholder=_("Radio show title*"),
    ),
    MultiFieldPanel(
        [
            FieldPanel("description"),
            FieldPanel("picture"),
        ],
        heading=_("Description"),
    ),
    MultiFieldPanel(
        [
            FieldPanel("contact_phone"),
            FieldPanel("contact_email"),
        ],
        heading=_("Contact"),
    ),
]

PodcastPage.base_form_class = PodcastPageForm
PodcastPage.content_panels = [
    TitleFieldPanel(
        "title",
        placeholder=_("Podcast title*"),
    ),
    MultiFieldPanel(
        [
            FieldPanel("description"),
            FieldPanel("picture"),
            FieldPanel("tags"),
        ],
        heading=_("Description"),
    ),
    MultiFieldPanel(
        [
            FieldRowPanel(
                [
                    FieldPanel(
                        "sound_type",
                        classname="col3",
                        disable_comments=True,
                    ),
                    FieldPanel(
                        "sound_file",
                        classname="col9",
                        widget=AdminClearableFileInput(
                            attrs={"data-action": "podcast-sound#retrieve"},
                        ),
                        attrs={"data-podcast-sound-target": "file"},
                    ),
                    FieldPanel(
                        "sound_external_url",
                        classname="col9",
                        widget=forms.URLInput(
                            attrs={"data-action": "podcast-sound#retrieve"},
                        ),
                        attrs={"data-podcast-sound-target": "url"},
                    ),
                ]
            ),
            FieldPanel(
                "duration",
                disable_comments=True,
                widget=forms.TimeInput(
                    attrs={
                        "readonly": True,
                        "title": _("The format must be HH:MM:SS"),
                        "data-podcast-sound-target": "duration",
                    },
                    format="%H:%M:%S",
                ),
            ),
        ],
        heading=_("Media"),
        attrs={"data-controller": "podcast-sound"},
    ),
    FieldPanel("publication_date"),
]
