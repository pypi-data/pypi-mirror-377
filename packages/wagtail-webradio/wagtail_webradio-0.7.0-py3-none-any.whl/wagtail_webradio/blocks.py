from django import forms
from django.utils.functional import cached_property
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from wagtail import blocks
from wagtail.coreutils import resolve_model_string


class BaseModelChoiceBlock(blocks.FieldBlock):
    """
    Abstract class for fields that implement a chooser interface for a
    model with a Select widget.
    """

    model_class = None

    def __init__(self, required=True, help_text=None, validators=(), **kwargs):
        self.field_options = {
            "required": required,
            "help_text": help_text,
            "validators": validators,
        }
        super().__init__(**kwargs)

    @cached_property
    def field(self):
        return forms.ModelChoiceField(
            queryset=self.get_queryset(),
            **self.field_options,
        )

    def to_python(self, value):
        if value is None:
            return value
        try:
            return self.model_class.objects.get(pk=value)
        except self.model_class.DoesNotExist:
            return None

    def get_prep_value(self, value):
        if value is None:
            return None
        return value.pk

    def value_from_form(self, value):
        if value is None or isinstance(value, self.model_class):
            return value
        try:
            return self.model_class.objects.get(pk=value)
        except (ValueError, TypeError, self.model_class.DoesNotExist):
            return None

    def get_queryset(self):
        """Return the queryset to use for the field."""
        return self.model_class.objects.all()


class RadioShowPageChooserBlock(BaseModelChoiceBlock):
    class Meta:
        label = _("Radio show")
        icon = "microphone"

    @cached_property
    def model_class(self):
        return resolve_model_string("wagtail_webradio.RadioShowPage")


class PodcastPageChooserBlock(blocks.ChooserBlock):
    class Meta:
        label = _("Podcast")
        icon = "headphone"

    @cached_property
    def model_class(self):
        return resolve_model_string("wagtail_webradio.PodcastPage")

    @cached_property
    def widget(self):
        from .widgets import AdminPodcastPageChooser

        return AdminPodcastPageChooser()

    def get_form_state(self, value):
        value_data = self.widget.get_value_data(value)
        if value_data is None:
            return None
        return {
            "id": value_data["id"],
            "parentId": value_data["parent_id"],
            "adminTitle": value_data["display_title"],
            "editUrl": value_data["edit_url"],
        }

    def render_basic(self, value, context=None):
        if value:
            return format_html('<a href="{0}">{1}</a>', value.url, value.title)
        return ""


class PodcastPageTagChooserBlock(BaseModelChoiceBlock):
    class Meta:
        label = _("Podcast tag")
        icon = "tag"

    @cached_property
    def tagged_model(self):
        return resolve_model_string("wagtail_webradio.TaggedPodcastPage")

    @cached_property
    def model_class(self):
        return self.tagged_model.tag_model()

    def get_queryset(self):
        return self.tagged_model.tags_for()
