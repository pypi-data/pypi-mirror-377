from django.test import RequestFactory, TestCase, override_settings

from cms.api import add_plugin

from djangocms_export_page.export.common import PageExport
from djangocms_export_page.export.docx import DocxPageExport

from .factories import AliasFactory, BlogFactory


class ExportModelTests(TestCase):
    def setUp(self):
        self.object = BlogFactory()
        self.language = "nl"
        self.request = RequestFactory().get(self.object.get_absolute_url())

        static_alias = AliasFactory(static_code="footer")
        self.static_placeholder = static_alias.get_placeholder(self.language)

    def test_model_export(self):
        export = DocxPageExport(self.request, self.object, language=self.language)
        export_file = export.export()
        self.assertEqual(type(export_file), bytes)

    def test_page_url(self):
        export = PageExport(self.request, self.object, language=self.language)
        self.assertEqual(
            export.page_url, "http://example.com" + self.object.get_absolute_url()
        )

    @override_settings(EXPORT_STATIC_ALIASES={"blog.html": ["footer"]})
    def test_page_with_placeholders(self):
        add_plugin(
            self.object.content, "TextPlugin", self.language, body="Body Content"
        )

        add_plugin(
            self.static_placeholder, "TextPlugin", self.language, body="footer info"
        )
        export = DocxPageExport(self.request, self.object, language=self.language)

        data = export.get_data()
        self.assertEqual(data[1].components[1].fields[0].value, "Body Content")
        self.assertEqual(data[2].components[0].fields[0].value, "footer info")
