from django.utils.translation import gettext_lazy

from . import __version__

try:
    from pretix.base.plugins import PluginConfig
except ImportError:
    raise RuntimeError("Please use pretix 2.7 or above to run this plugin!")


class PluginApp(PluginConfig):
    default = True
    name = "pretix_homepage"
    verbose_name = "Home Page"

    class PretixPluginMeta:
        name = gettext_lazy("Home Page")
        author = "Diptangshu Chakrabarty"
        description = gettext_lazy("A home page for self hosted Pretix")
        visible = True
        version = __version__
        category = "CUSTOMIZATION"
        compatibility = "pretix>=2.7.0"
        settings_links = []
        navigation_links = []

    def ready(self):
        from . import signals  # NOQA
