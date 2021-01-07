import graphene

# from ..core.auth import login_required
from .mutations import CreateCard


class PaymentMutations(graphene.ObjectType):
    create_card = CreateCard.Field()
