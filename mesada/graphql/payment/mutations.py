import graphene

from ...payment import create_card
from ..core.mutations import BaseMutation


class BillingDetailsInput(graphene.InputObjectType):
    name = graphene.String(description="Full name of the card holder", required=True)
    city = graphene.String(required=True)
    country = graphene.String(
        description="Country portion of the address. Formatted as a two-letter country code",
        required=True,
    )
    line1 = graphene.String(description="Line one of the street address", required=True)
    line2 = graphene.String(description="Line two of the street address")
    district = graphene.String(
        description="Region portion of the address. If the country is US or Canada district is required and should use the two-letter code for the subdivision."
    )
    postal_code = graphene.String(description="ZIP code of the address", required=True)


class CardInput(graphene.InputObjectType):
    encrypted_data = graphene.String(description="Card encrypted data", required=True)
    key_id = graphene.String(description="Encryption key", required=True)
    exp_month = graphene.Int(description="Card expiration month", required=True)
    exp_year = graphene.Int(description="Card expiration year", required=True)
    billing_details = BillingDetailsInput(description="Card billing details")


class CreateCard(BaseMutation):
    response = graphene.JSONString()

    class Arguments:
        input = CardInput(description="Card input", required=True)

    class Meta:
        description = "Save a new card withing the Circle API."

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        obj = CreateCard()
        print(data)
        ip_address = info.context.META.get("REMOTE_ADDR")
        session = info.context.session
        body = {}

        response = create_card(body)

        print(ip_address)
        print(str(session.session_key))

        setattr(obj, "response", response.json())
        return obj
