import graphene

# from ..core.auth import login_required
from .mutations import CreateCard, CreatePublicKey, ProcessorTokenCreate


class PaymentMutations(graphene.ObjectType):
    create_card = CreateCard.Field()
    create_public_key = CreatePublicKey.Field()

class PaymentMethodsMutations(graphene.ObjectType):
    processor_token_create = ProcessorTokenCreate.Field()

