import logging
from django.shortcuts import render
from pretix.base.models import Organizer

logger = logging.getLogger("pretix.plugins.homepage")


def index_view(request, *args, **kwargs):
    logger.debug("rendering home page")

    orgs = Organizer.objects.all()
    logger.debug("orgs: %s", orgs)

    r = render(request, "pretix_homepage/index.html")
    r._csp_ignore = True
    return r
