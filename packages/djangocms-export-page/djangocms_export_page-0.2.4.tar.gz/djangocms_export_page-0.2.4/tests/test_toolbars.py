from django.urls import reverse

from cms.test_utils.testcases import CMSTestCase
from cms.toolbar.items import LinkItem
from cms.toolbar.toolbar import CMSToolbar

from djangocms_export_page.constants import DOCX


class ToolbarsTests(CMSTestCase):

    def setUp(self):

        super().setUp()
        self.user = self.get_superuser()

    def test_page_with_one_(self):

        page = self.create_homepage("title", "test.html", "en")

        request = self.get_page_request(page, self.user)
        toolbar = CMSToolbar(request)
        toolbar.populate()

        url = reverse(
            "export-page:cms_page",
            kwargs={
                "page_pk": page.pk,
                "file_format": DOCX,
            },
        )

        page_menu = toolbar.get_menu("page")
        page_links = page_menu.find_items(LinkItem, url=url)
        self.assertEqual(len(page_links), 1)
