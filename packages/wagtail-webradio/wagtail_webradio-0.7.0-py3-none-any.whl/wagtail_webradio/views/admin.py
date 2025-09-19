from django import forms
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.urls import path, reverse
from django.utils.functional import cached_property, classproperty
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy

from wagtail.admin.filters import (
    DateRangePickerWidget,
    PopularTagsFilter,
    WagtailFilterSet,
)
from wagtail.admin.ui.tables import Column, DateColumn
from wagtail.admin.ui.tables.pages import (
    BulkActionsColumn,
    NavigateToChildrenColumn,
    PageStatusColumn,
    PageTitleColumn,
)
from wagtail.admin.views.pages.listing import IndexView
from wagtail.admin.viewsets.pages import PageListingViewSet

from django_filters.filters import DateFromToRangeFilter

from wagtail_webradio.models import (
    PodcastPage,
    RadioShowPage,
    TaggedPodcastPage,
)


class NavigateToPodcastsColumn(NavigateToChildrenColumn):
    cell_template_name = (
        "wagtail_webradio/admin/tables/navigate_to_podcasts_cell.html"
    )


class PodcastPageFilterSet(WagtailFilterSet):
    publication_date = DateFromToRangeFilter(
        label=gettext_lazy("Publication date"),
        widget=DateRangePickerWidget,
    )

    class Meta:
        model = PodcastPage
        fields = []

    def __init__(self, *args, is_searching=None, **kwargs):
        super().__init__(*args, **kwargs)

        popular_tags = list(
            TaggedPodcastPage.tags_for()
            .annotate(item_count=Count(TaggedPodcastPage.tag_relname()))
            .order_by("-item_count")[:10]
        )

        if popular_tags:
            self.filters["tag"] = PopularTagsFilter(
                label=_("Tag"),
                field_name="tags__name",
                choices=[(tag.name, tag.name) for tag in popular_tags],
                widget=forms.CheckboxSelectMultiple,
                use_subquery=is_searching,
                help_text=_("Filter by up to ten most popular tags."),
            )


class PodcastPageIndexView(IndexView):
    model = PodcastPage
    header_icon = "headphone"
    filterset_class = PodcastPageFilterSet

    columns = [
        BulkActionsColumn("bulk_actions"),
        PageTitleColumn(
            "title",
            label=gettext_lazy("Title"),
            sort_key="title",
            classname="title",
        ),
        Column(
            "get_duration_display",
            label=gettext_lazy("Duration"),
            sort_key="duration",
            width="12%",
        ),
        DateColumn(
            "publication_date",
            label=gettext_lazy("Publication date"),
            sort_key="publication_date",
            width="12%",
        ),
        DateColumn(
            "latest_revision_created_at",
            label=gettext_lazy("Updated"),
            sort_key="latest_revision_created_at",
            width="12%",
        ),
        PageStatusColumn(
            "status",
            label=gettext_lazy("Status"),
            sort_key="live",
            width="12%",
        ),
    ]

    radio_show_index_url_name = None

    def get(self, request, radio_show_page_id):
        self.radio_show_page = get_object_or_404(
            RadioShowPage.objects.all(),
            pk=radio_show_page_id,
        )
        return super().get(request)

    def get_base_queryset(self):
        pages = self.radio_show_page.podcasts.filter(
            pk__in=self.permission_policy.explorable_instances(
                self.request.user
            ).values_list("pk", flat=True)
        )
        pages = self.annotate_queryset(pages)
        return pages

    def get_page_subtitle(self):
        return self.radio_show_page.title

    def get_header_title(self):
        return _("Podcasts of: %(radio_show)s") % {
            "radio_show": self.radio_show_page.title
        }

    def get_breadcrumbs_items(self):
        return self.breadcrumbs_items + [
            {
                "url": self.radio_show_index_url,
                "label": _("Radio shows"),
            },
            {
                "url": (
                    reverse(
                        "wagtailadmin_pages:edit",
                        args=(self.radio_show_page.pk,),
                    )
                    if self.user_has_permission_for_instance(
                        "change", self.radio_show_page
                    )
                    else None
                ),
                "label": self.radio_show_page.title,
            },
            {
                "url": "",
                "label": self.get_page_title(),
                "sublabel": self.get_page_subtitle(),
            },
        ]

    def get_index_url(self):
        return reverse(
            self.index_url_name,
            args=(self.radio_show_page.pk,),
        )

    def get_index_results_url(self):
        return reverse(
            self.index_results_url_name,
            args=(self.radio_show_page.pk,),
        )

    def get_add_url(self):
        if self.user_has_permission_for_instance("add", self.radio_show_page):
            return reverse(
                "wagtailadmin_pages:add",
                kwargs={
                    "content_type_app_name": self.model._meta.app_label,
                    "content_type_model_name": self.model._meta.model_name,
                    "parent_page_id": self.radio_show_page.pk,
                },
            )

    def get_radio_show_index_url(self):
        return reverse(self.radio_show_index_url_name)

    @cached_property
    def radio_show_index_url(self):
        return self.get_radio_show_index_url()

    def get_filterset_kwargs(self):
        kwargs = super().get_filterset_kwargs()
        kwargs["is_searching"] = self.is_searching
        return kwargs


class RadioShowPageListingViewSet(PageListingViewSet):
    icon = "microphone"
    menu_label = gettext_lazy("Radio shows")
    model = RadioShowPage
    filterset_class = None

    podcast_index_view_class = PodcastPageIndexView

    @classproperty
    def columns(cls):
        return [
            *PageListingViewSet.columns,
            NavigateToPodcastsColumn("navigate", width="10%"),
        ]

    def get_index_view_kwargs(self, **kwargs):
        return super().get_index_view_kwargs(
            **{
                "add_item_label": _("Add a radio show"),
                "default_ordering": "title",
                **kwargs,
            }
        )

    def get_choose_parent_view_kwargs(self, **kwargs):
        return super().get_choose_parent_view_kwargs(
            **{
                "submit_button_label": _("Create a new radio show"),
                **kwargs,
            }
        )

    def get_podcast_index_view_kwargs(self, **kwargs):
        return {
            "add_item_label": _("Add a podcast"),
            "index_url_name": self.get_url_name("podcast_index"),
            "index_results_url_name": self.get_url_name(
                "podcast_index_results"
            ),
            "radio_show_index_url_name": self.get_url_name("index"),
            "default_ordering": "-publication_date",
            **kwargs,
        }

    @property
    def podcast_index_view(self):
        return self.podcast_index_view_class.as_view(
            **self.get_podcast_index_view_kwargs()
        )

    @property
    def podcast_index_results_view(self):
        return self.podcast_index_view_class.as_view(
            **self.get_podcast_index_view_kwargs(),
            results_only=True,
        )

    def get_urlpatterns(self):
        return super().get_urlpatterns() + [
            path(
                "<int:radio_show_page_id>/podcasts/",
                self.podcast_index_view,
                name="podcast_index",
            ),
            path(
                "<int:radio_show_page_id>/podcasts/results/",
                self.podcast_index_results_view,
                name="podcast_index_results",
            ),
        ]
