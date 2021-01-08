import graphene
from graphene_django.types import ObjectType
from ..core.auth import login_required
from ...payment.models import PaymentMethods
from .types import PaymentMethod
from .mutations import CreateCard, CreatePublicKey, ProcessorTokenCreate


class PaymentMethodsQueries(graphene.ObjectType):
    payment_method = graphene.Field(PaymentMethod, id=graphene.Int(), description="Get payment method by id")
    user_payment_methods = graphene.List(
        PaymentMethod, user_id=graphene.Int(), description="Get list of payment methods of given user"
    )

    @login_required
    def resolve_payment_method(self, _info, **kwargs):
        _id = kwargs.get("id")
        return PaymentMethods.objects.get(pk=_id)

    @login_required
    def resolve_payment_methods(self, _info, user_id):
        return PaymentMethods.objects.filter(user__id=user_id)


class PaymentMutations(graphene.ObjectType):
    create_card = CreateCard.Field()
    create_public_key = CreatePublicKey.Field()


class PaymentMethodsMutations(graphene.ObjectType):
    processor_token_create = ProcessorTokenCreate.Field()
