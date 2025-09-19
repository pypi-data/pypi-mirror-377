from django.utils.translation import gettext_lazy as _

from wagtail import hooks
from wagtail.admin.menu import Menu, SubmenuMenuItem

from .views.admin import RadioShowPageListingViewSet

webradio_menu = Menu(register_hook_name="register_webradio_menu_item")

radio_show_page_listing_viewset = RadioShowPageListingViewSet(
    "webradioadmin_radioshows",
    url_prefix="webradio/radio-shows",
    menu_order=10,
    menu_hook="register_webradio_menu_item",
)


@hooks.register("register_admin_viewset")
def register_radio_show_page_listing_viewset():
    return radio_show_page_listing_viewset


@hooks.register("register_admin_menu_item")
def register_webradio_menu():
    return SubmenuMenuItem(
        _("Web radio"),
        webradio_menu,
        icon_name="broadcast",
        name="webradio",
        order=410,
    )


@hooks.register("register_icons")
def register_icons(icons):
    for icon in ["broadcast", "headphone", "microphone"]:
        icons.append(f"wagtail_webradio/icons/{icon}.svg")
    return icons
