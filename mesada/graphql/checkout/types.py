from graphene_django.types import DjangoObjectType

from ...checkout.models import Checkout


class Checkout(DjangoObjectType):
    class Meta:
        description = "Represets a Checkout"
        model = Checkout
        fields = "__all__"
