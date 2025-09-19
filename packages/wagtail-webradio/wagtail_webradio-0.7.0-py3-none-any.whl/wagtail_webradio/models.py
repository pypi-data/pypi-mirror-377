import os.path

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from wagtail.fields import RichTextField
from wagtail.models import Page, PageManager, PageQuerySet

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from taggit.models import TaggedItemBase

from .utils import format_duration
from .validators import validate_audio_file_type

DESCRIPTION_EDITOR_FEATURES = ["bold", "italic", "link", "ol", "ul"]

PODCAST_SOUND_DIR = "podcasts"


def upload_podcast_sound_to(instance, filename):
    """Return the upload path of a Podcast sound file."""
    filename = f"{instance.slug}{os.path.splitext(filename)[1]}"

    return (
        os.path.join(PODCAST_SOUND_DIR, instance.radio_show.slug, filename)
        if getattr(settings, "WEBRADIO_SOUND_PATH_BY_RADIOSHOW", False)
        else os.path.join(PODCAST_SOUND_DIR, filename)
    )


class AbstractRadioShowIndexPage(Page):
    subpage_types = ["wagtail_webradio.RadioShowPage"]

    class Meta:
        abstract = True
        verbose_name = _("radio shows index")
        verbose_name_plural = _("radio shows indexes")

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["radio_shows"] = RadioShowPage.objects.child_of(self).live()
        return context


class RadioShowPage(Page):
    description = RichTextField(
        verbose_name=_("description"),
        blank=True,
        features=DESCRIPTION_EDITOR_FEATURES,
    )
    picture = models.ForeignKey(
        "wagtailimages.Image",
        verbose_name=_("picture"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    contact_phone = models.CharField(
        verbose_name=_("phone number"),
        blank=True,
        max_length=20,
    )
    contact_email = models.EmailField(verbose_name=_("email"), blank=True)

    # Page configuration

    show_in_menus_default = True
    subpage_types = ["wagtail_webradio.PodcastPage"]

    class Meta:
        verbose_name = _("radio show")
        verbose_name_plural = _("radio shows")

    @property
    def podcasts(self):
        return PodcastPage.objects.child_of(self)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["podcasts"] = self.podcasts.live().order_by("-publication_date")
        return context


class TaggedPodcastPage(TaggedItemBase):
    content_object = ParentalKey(
        "PodcastPage",
        on_delete=models.CASCADE,
        related_name="podcast_tags",
    )

    @classmethod
    def tags_for(cls, model=None, instance=None, **extra_filters):
        # 'model' is required as a positional argument by django-taggit - but
        # it is not used. We set it for convenience as it should not change.
        if model is None:
            model = PodcastPage
        return super().tags_for(model, instance=instance, **extra_filters)


class PodcastPageQuerySet(PageQuerySet):
    def live_q(self):
        return super().live_q() & Q(publication_date__lte=timezone.now())


PodcastPageManager = PageManager.from_queryset(PodcastPageQuerySet)


class PodcastPage(Page):
    description = RichTextField(
        verbose_name=_("description"),
        blank=True,
        features=DESCRIPTION_EDITOR_FEATURES,
    )
    picture = models.ForeignKey(
        "wagtailimages.Image",
        verbose_name=_("picture"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    tags = ClusterTaggableManager(
        through=TaggedPodcastPage,
        verbose_name=_("tags"),
        blank=True,
    )

    sound_file = models.FileField(
        upload_to=upload_podcast_sound_to,
        validators=[validate_audio_file_type],
        verbose_name=_("sound file"),
        null=True,
        blank=True,
    )
    sound_external_url = models.URLField(
        verbose_name=_("sound external URL"),
        blank=True,
    )
    duration = models.DurationField(
        verbose_name=_("duration"),
        blank=True,
        null=True,
    )

    publication_date = models.DateField(
        verbose_name=_("publication date"),
        default=timezone.now,
    )

    objects = PodcastPageManager()

    # Page configuration

    parent_page_types = ["wagtail_webradio.RadioShowPage"]
    subpage_types = []

    class Meta:
        verbose_name = _("podcast")
        verbose_name_plural = _("podcasts")

    @property
    def radio_show(self):
        return self.get_parent()

    @property
    def sound_url(self):
        if self.sound_file:
            return self.sound_file.url
        return self.sound_external_url

    def get_duration_display(self):
        return format_duration(self.duration)


# ------------------------------------------------------------------------------


class RadioShow(models.Model):
    title = models.CharField(verbose_name=_("title"), max_length=255)

    description = RichTextField(
        verbose_name=_("description"),
        blank=True,
        features=DESCRIPTION_EDITOR_FEATURES,
    )
    picture = models.ForeignKey(
        "wagtailimages.Image",
        verbose_name=_("picture"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    contact_phone = models.CharField(
        verbose_name=_("phone number"),
        blank=True,
        max_length=20,
    )
    contact_email = models.EmailField(verbose_name=_("email"), blank=True)

    slug = models.SlugField(
        verbose_name=_("slug"),
        max_length=255,
        unique=True,
    )

    class Meta:
        verbose_name = _("radio show")
        verbose_name_plural = _("radio shows")

    def __str__(self):
        return self.title


class TaggedPodcast(TaggedItemBase):
    content_object = ParentalKey(
        "Podcast",
        on_delete=models.CASCADE,
        related_name="podcast_tags",
    )


class Podcast(ClusterableModel):
    title = models.CharField(verbose_name=_("title"), max_length=255)

    description = RichTextField(
        verbose_name=_("description"),
        blank=True,
        features=DESCRIPTION_EDITOR_FEATURES,
    )
    picture = models.ForeignKey(
        "wagtailimages.Image",
        verbose_name=_("picture"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    tags = ClusterTaggableManager(
        through=TaggedPodcast,
        verbose_name=_("tags"),
        blank=True,
    )

    sound_file = models.FileField(
        upload_to=upload_podcast_sound_to,
        validators=[validate_audio_file_type],
        verbose_name=_("sound file"),
        null=True,
        blank=True,
    )
    sound_url = models.URLField(
        verbose_name=_("sound URL"),
        blank=True,
    )
    duration = models.DurationField(
        verbose_name=_("duration"),
        blank=True,
        null=True,
    )

    radio_show = models.ForeignKey(
        "RadioShow",
        verbose_name=_("radio show"),
        on_delete=models.PROTECT,
        related_name="podcasts",
        related_query_name="podcast",
    )

    publish_date = models.DateTimeField(
        verbose_name=_("publish date"),
        default=timezone.now,
    )
    slug = models.SlugField(
        verbose_name=_("slug"),
        max_length=255,
        unique=True,
    )

    class Meta:
        ordering = ["-publish_date"]
        verbose_name = _("podcast")
        verbose_name_plural = _("podcasts")

    def __str__(self):
        return self.title

    def get_duration_display(self):
        return format_duration(self.duration)

    def get_picture(self):
        return self.picture or self.radio_show.picture

    @property
    def url(self):
        return self.sound_file.url if self.sound_file else self.sound_url
