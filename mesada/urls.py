"""mesada URL Configuration"""

from django.conf.urls import re_path
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

# from .data_feeds.urls import urlpatterns as feed_urls
from .graphql.api import schema
from .graphql.views import GraphQLView

# from .plugins.views import handle_plugin_webhook
# from .product.views import digital_product

urlpatterns = [
    re_path(r"^graphql/", csrf_exempt(GraphQLView.as_view(schema=schema)), name="api"),
    path("", lambda request: HttpResponse("hello"), name="hello"),
]
