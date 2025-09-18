from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from cms.cms_toolbars import PAGE_MENU_IDENTIFIER
from cms.toolbar.items import Break
from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool
from cms.utils.page_permissions import user_can_change_page

from .constants import FILE_FORMATS


@toolbar_pool.register
class ExportPageToolbar(CMSToolbar):

    def populate(self):
        page = self.request.current_page

        if not page or not user_can_change_page(self.request.user, page=page):
            return

        current_page_menu = self.toolbar.get_or_create_menu(PAGE_MENU_IDENTIFIER)
        position = self.get_position(current_page_menu)

        file_formats = FILE_FORMATS.values()

        if len(file_formats) == 1:
            menu = current_page_menu
        else:
            menu = current_page_menu.get_or_create_menu(
                "export-page", _("Export"), position=position
            )

        for file_format in file_formats:
            label = _("Export to {ext}").format(ext="." + file_format.ext)
            url = reverse(
                "export-page:cms_page",
                kwargs={"page_pk": page.pk, "file_format": file_format.name},
            )
            menu.add_link_item(label, url=url, position=position)

        current_page_menu.add_break("export-page-break", position=position)

    def get_position(self, menu):
        # Last separator
        breaks = menu.find_items(Break)
        if breaks:
            return breaks[-1].index
        return None
