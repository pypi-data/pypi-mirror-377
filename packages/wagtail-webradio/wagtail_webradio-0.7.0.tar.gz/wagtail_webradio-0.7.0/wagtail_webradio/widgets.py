from django.forms import widgets
from django.utils.translation import gettext_lazy as _

from wagtail.admin.widgets import AdminPageChooser, BaseChooser

from .models import PodcastPage


class AdminClearableFileInput(widgets.ClearableFileInput):
    initial_text = _("Currently:")
    template_name = "wagtail_webradio/admin/widgets/clearable_file_input.html"

    class Media:
        css = {"all": ("wagtail_webradio/admin/css/clearable_file_input.css",)}


class AdminPodcastPageChooser(AdminPageChooser):
    choose_one_text = _("Choose a podcast")
    choose_another_text = _("Choose another podcast")
    link_to_chosen_text = _("Edit this podcast")
    icon = "headphone"
    model = PodcastPage

    model_names = ["wagtail_webradio.PodcastPage"]
    can_choose_root = False

    def __init__(self, user_perms=None, **kwargs):
        BaseChooser.__init__(self, **kwargs)

        self.user_perms = user_perms
