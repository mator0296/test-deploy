import graphene
from graphene_django.types import ObjectType
from ..core.auth import login_required
from ...payment.models import PaymentMethods
from .types import PaymentMethodType


class PaymentMethodsQueries(ObjectType):
    payment_method = graphene.Field(PaymentMethodType, id=graphene.Int())
    user_payment_methods = graphene.List(PaymentMethodType, user_id=graphene.Int())

    @login_required
    def resolve_payment_method(self, _info, **kwargs):
        _id = kwargs.get("id")
        return PaymentMethods.objects.get(pk=_id)

    @login_required
    def resolve_user_payment_methods(self, _info, user_id):
        return PaymentMethods.objects.filter(user__id=user_id)
