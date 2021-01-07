import graphene

from .mutations import (
    CreateCard,
    CreateLinkToken,
    CreatePublicKey,
    ProcessorTokenCreate,
)


class PaymentMutations(graphene.ObjectType):
    create_card = CreateCard.Field()
    create_link_token = CreateLinkToken.Field()
    create_public_key = CreatePublicKey.Field()


class PaymentMethodsMutations(graphene.ObjectType):
    processor_token_create = ProcessorTokenCreate.Field()
