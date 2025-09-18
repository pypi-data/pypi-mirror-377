import sys
from warnings import warn

from django.conf import settings


class _Settings(object):

    _placeholder_dep_msg = (
        "Static Placeholders are disabled form Django CMS 4. "
        "Pleas use djangocms-alias's static_alias "
        "and use the EXPORT_STATIC_ALIASES setting"
    )

    @property
    def EXPORT_STATIC_PLACEHOLDERS(self):

        warn(self._placeholder_dep_msg, DeprecationWarning, stacklevel=2)

        setting = getattr(settings, "EXPORT_STATIC_PLACEHOLDERS", {})
        return setting

    @property
    def EXPORT_STATIC_ALIASES(self):

        old_setting = getattr(settings, "EXPORT_STATIC_PLACEHOLDERS", {})

        if old_setting:
            warn(self._placeholder_dep_msg, DeprecationWarning, stacklevel=2)

            return old_setting

        return getattr(settings, "EXPORT_STATIC_ALIASES", {})

    def __getattr__(self, name):
        return globals()[name]


# other parts of itun that you WANT to code in
# module-ish ways
sys.modules[__name__] = _Settings()
