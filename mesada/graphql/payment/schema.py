import graphene
from graphene_django.types import ObjectType
from ..core.auth import login_required
from ...payment.models import PaymentMethods
from .types import PaymentMethodType


class PaymentMethodsQueries(ObjectType):
    paymentMethod = graphene.Field(PaymentMethodType, id=graphene.Int())
    userPaymentMethods = graphene.List(
        PaymentMethodType, user_id=graphene.Int()
    )

    @login_required
    def resolve_payment_method(self, _info, **kwargs):
        _id = kwargs.get("id")

        if _id is not None:
            return PaymentMethods.objects.get(pk=_id)

        return None

    @login_required
    def resolve_user_payment_methods(self, _info, user_id):
        if user_id is not None:
            PaymentMethods.objects.filter(user__id=user_id)

        return None
