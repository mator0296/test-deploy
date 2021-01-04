from graphene_django.types import DjangoObjectType
from ...payment.models import PaymentMethods


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
