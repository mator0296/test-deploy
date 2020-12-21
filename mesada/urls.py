"""mesada URL Configuration"""

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib.staticfiles.views import serve
from django.views.decorators.csrf import csrf_exempt

# from .data_feeds.urls import urlpatterns as feed_urls
from .graphql.api import schema
from .graphql.views import GraphQLView

# from .plugins.views import handle_plugin_webhook
# from .product.views import digital_product

urlpatterns = [
    url(r"^graphql/", csrf_exempt(GraphQLView.as_view(schema=schema)), name="api")
]
