import graphene

from ...payment import create_card
from ..core.mutations import BaseMutation
from .types import BillingDetailsInput, Card


class CardInput(graphene.InputObjectType):
    encrypted_data = graphene.String(description="Card encrypted data", required=True)
    key_id = graphene.String(description="Encryption key", required=True)
    exp_month = graphene.Int(description="Card expiration month", required=True)
    exp_year = graphene.Int(description="Card expiration year", required=True)
    billing_details = BillingDetailsInput(description="Card billing details")


class CreateCard(BaseMutation):
    response = graphene.JSONString()
    card = graphene.Field(Card)

    class Arguments:
        input = CardInput(description="Card input", required=True)

    class Meta:
        description = "Save a new card withing the Circle API."

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        print(info.context.user.is_authenticated)
        card = data.get("input")
        billing_details = card.get("billing_details")
        if not billing_details:
            # TODO: get the billing details from user's address
            pass

        ip_address = info.context.META.get("REMOTE_ADDR")
        session = info.context.session
        body = {
            "idempotencyKey": "",
            "keyId": card.get("key_id"),
            "encryptedData": card.get("encrypted_data"),
            "billingDetails": billing_details,
            "expMonth": card.get("expo_month"),
            "expYear": card.get("expo_year"),
            "metadata": {
                "sessionId": session.session_key,
                "ipAddress": ip_address
            }
        }

        response = create_card(body)
        return cls(response=response.json(), card=card)
