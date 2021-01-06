import graphene

# from ..core.auth import login_required
from .mutations import CreateCard, CreateProcessorToken


class PaymentMutations(graphene.ObjectType):
    create_card = CreateCard.Field()


class PaymentMethodsMutation(graphene.ObjectType):
    create_processor_token = CreateProcessorToken.Field()
