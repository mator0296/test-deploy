import graphene

# from ..core.auth import login_required
from .mutations import CreateCard, CreatePublicKey


class PaymentMutations(graphene.ObjectType):
    create_card = CreateCard.Field()
    create_public_key = CreatePublicKey.Field()
