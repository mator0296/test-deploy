from graphene_django.types import DjangoObjectType
from ..payment.models import PaymentMethods
from ..account.models import User


class PaymentMethodType(DjangoObjectType):
    class Meta:
        model = PaymentMethods
        fields = (
            "id",
            "type",
            "name",
            "exp_month",
            "exp_year",
            "network",
            "last_digits",
            "fingerprint",
            "user",
        )


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id",)
