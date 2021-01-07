import graphene

# from ..core.auth import login_required
from .mutations import CreateCard, CreateLinkToken


class PaymentMutations(graphene.ObjectType):
    create_card = CreateCard.Field()
    create_link_token = CreateLinkToken.Field()
