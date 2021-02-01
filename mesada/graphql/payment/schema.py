import graphene
from graphene.relay import Node

from ...payment.models import PaymentMethods
from ..core.auth import login_required
from .mutations import (
    CreateCard,
    CreateLinkToken,
    CreatePayment,
    CreatePublicKey,
    RegisterAchPayment,
)
from .types import PaymentMethod


class PaymentMethodsQueries(graphene.ObjectType):
    payment_method = graphene.Field(
        PaymentMethod, id=graphene.ID(), description="Get payment method by id"
    )
    payment_methods = graphene.List(
        PaymentMethod, description="Get list of payment methods of given user"
    )

    @login_required
    def resolve_payment_method(self, _info, id):
        _, payment_id = Node.from_global_id(id)
        return PaymentMethods.objects.get(pk=payment_id)

    @login_required
    def resolve_payment_methods(self, _info):
        user = _info.context.user
        return PaymentMethods.objects.filter(user__id=user.id)


class PaymentMutations(graphene.ObjectType):
    create_card = CreateCard.Field()
    create_link_token = CreateLinkToken.Field()
    create_public_key = CreatePublicKey.Field()
    create_payment = CreatePayment.Field()


class PaymentMethodsMutations(graphene.ObjectType):
    register_ach_payment = RegisterAchPayment.Field()
