import graphene
from requests import Response

from ..core.mutations import BaseMutation
from ...payment import create_card


class CardInput(graphene.InputObjectType):
    encrypted_data = graphene.String(description="Card encrypted data", required=True)
    key_id = graphene.String(description="Encryption key", required=True)
    exp_month = graphene.Int(description="Card expiration month", required=True)
    exp_year = graphene.Int(description="Card expiration year", required=True)


class CreateCard(BaseMutation):
    response = graphene.JSONString()

    class Arguments:
        input = CardInput(description="Card input", required=True)

    class Meta:
        description = "Save a new card withing the Circle API."

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        obj = CreateCard()

        ip_address = info.context.META.get("REMOTE_ADDR")
        session = info.context.session
        body = {}

        response = create_card(body)

        print(ip_address)
        print(str(session.session_key))

        setattr(obj, "response", response.json())
        return obj
