"""mesada URL Configuration"""

from django.conf.urls import include, re_path, url
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .graphql.api import schema
from .graphql.views import GraphQLView

urlpatterns = [
    re_path(r"^graphql/", csrf_exempt(GraphQLView.as_view(schema=schema)), name="api"),
    url(r"^admin/", admin.site.urls),
    url(r"^admin_tools/", include("admin_tools.urls")),
    path("", lambda request: HttpResponse("hello"), name="hello"),
]
