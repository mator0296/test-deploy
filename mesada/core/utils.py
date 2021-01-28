from uuid import uuid4

from django.conf import settings
from django.contrib.sites.models import Site
from urllib.parse import urljoin
from django.utils.encoding import iri_to_uri


def get_client_ip(request):
    ip = request.META.get("HTTP_X_FORWARDED_FOR", None)
    if ip:
        return ip.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", None)

def generate_idempotency_key():
    return str(uuid4())


def build_absolute_uri(location):
    # type: (str) -> str
    host = Site.objects.get_current().domain
    protocol = "https" if settings.ENABLE_SSL else "http"
    current_uri = "%s://%s" % (protocol, host)
    location = urljoin(current_uri, location)
    return iri_to_uri(location)
