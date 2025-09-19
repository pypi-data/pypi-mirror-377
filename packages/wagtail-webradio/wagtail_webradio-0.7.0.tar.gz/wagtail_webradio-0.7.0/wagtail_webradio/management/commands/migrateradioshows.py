from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from wagtail.models import Page

from wagtail_webradio.models import (
    Podcast,
    PodcastPage,
    RadioShow,
    RadioShowPage,
)


class Command(BaseCommand):
    help = (
        "Transforms RadioShow and Podcast objects to pages. If an error "
        "occurs, changes are rolled back."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Delete objects once migrated.",
        )
        parser.add_argument(
            "parent_page_id",
            type=int,
            help="Parent page ID for new radio show pages.",
        )

    def handle(self, *args, **options):
        parent_page_id = options["parent_page_id"]
        delete_objects = options.get("delete", False)

        try:
            parent_page = Page.objects.get(pk=parent_page_id)
        except Page.DoesNotExist as exc:
            raise CommandError(
                "Page with id '%d' does not exist." % parent_page_id
            ) from exc

        with transaction.atomic():
            radio_shows = RadioShow.objects.all()

            if not radio_shows:
                self.stdout.write("No RadioShow object to migrate.")
                return

            for radio_show in radio_shows:
                podcasts = Podcast.objects.filter(radio_show=radio_show)

                self.stdout.write(
                    "Migrating '%s' and its %d podcasts…"
                    % (radio_show.title, len(podcasts)),
                    ending="",
                )
                self.stdout.flush()

                radio_show_page = RadioShowPage(
                    title=radio_show.title,
                    description=radio_show.description,
                    picture=radio_show.picture,
                    contact_phone=radio_show.contact_phone,
                    contact_email=radio_show.contact_email,
                    slug=radio_show.slug,
                )
                parent_page.add_child(instance=radio_show_page)

                for podcast in podcasts:
                    podcast_page = PodcastPage(
                        title=podcast.title,
                        description=podcast.description,
                        picture=podcast.picture,
                        sound_file=podcast.sound_file,
                        sound_external_url=podcast.sound_url,
                        duration=podcast.duration,
                        publication_date=podcast.publish_date,
                        slug=podcast.slug,
                    )
                    radio_show_page.add_child(instance=podcast_page)

                    if podcast.tags.exists():
                        podcast_page.tags.add(*podcast.tags.all())
                        podcast_page.save()

                if delete_objects:
                    podcasts.delete()
                    radio_show.delete()

                self.stdout.write(self.style.SUCCESS(" OK"))
