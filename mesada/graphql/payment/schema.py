import graphene
from graphene_django.types import ObjectType

from ...payment.models import PaymentMethods
from .types import PaymentMethodType


class PaymentMethodsQueries(ObjectType):
    paymentMethod = graphene.Field(PaymentMethodType, id=graphene.Int())
    userPaymentMethods = graphene.List(PaymentMethodType, user_id=graphene.Int())

    def resolve_payment_method(self, info, **kwargs):
        _id = kwargs.get("id")

        if info.context.user.is_authenticated() and _id is not None:
            return PaymentMethods.objects.get(pk=_id)

        return None

    def resolve_user_payment_methods(self, info, user_id):
        if info.context.user.is_authenticated() and user_id is not None:
            PaymentMethods.objects.filter(user__id=user_id)

        return None
