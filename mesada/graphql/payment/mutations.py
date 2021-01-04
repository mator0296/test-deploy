import graphene
import hashlib

from graphql.error.base import GraphQLError
from requests.exceptions import RequestException
from ...core.utils import generate_idempotency_key
from ...payment import create_card
from ...payment.models import paymentMethods, verificationAvs, verificationCvv
from ..core.mutations import ModelMutation
from .types import BillingDetailsInput, PaymentMethod
from .utils import get_default_billing_details, hash_session_id


class CardInput(graphene.InputObjectType):
    encrypted_data = graphene.String(description="Card encrypted data", required=True)
    key_id = graphene.String(description="Encryption key", required=True)
    exp_month = graphene.Int(description="Card expiration month", required=True)
    exp_year = graphene.Int(description="Card expiration year", required=True)
    billing_details = BillingDetailsInput(description="Card billing details")


class CreateCard(ModelMutation):
    payment_method = graphene.Field(PaymentMethod)

    class Meta:
        description = "Save a new card withing the Circle API."
        model = paymentMethods

    class Arguments:
        input = CardInput(description="Card input", required=True)

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        card = data.get("input")
        billing_details = card.get("billing_details")
        if not billing_details:
            billing_details = get_default_billing_details(info.context.user)
        if not info.context.session.session_key:
            info.context.session.save()

        ip_address = info.context.META.get("REMOTE_ADDR")
        hashed_session_id = hash_session_id(info.context.session.session_key)

        body = {
            "idempotencyKey": generate_idempotency_key(),
            "keyId": card.get("key_id"),
            "encryptedData": card.get("encrypted_data"),
            "billingDetails": billing_details,
            "expMonth": card.get("expo_month"),
            "expYear": card.get("expo_year"),
            "metadata": {
                "email": info.context.user.email,
                "phoneNumber": str(info.context.user.phone),
                "sessionId": hashed_session_id,
                "ipAddress": ip_address,
            },
        }

        response = create_card(body)

        data = response.json().get("data")
        billing_details = data.get("billingDetails")
        verification = data.get("verification")
        metadata = data.get("metadata")

        payment_method = paymentMethods.objects.create(
            type="CARD",
            exp_month=data.get("expMonth"),
            exp_year=data.get("expYear"),
            network=data.get("network"),
            last_digits=data.get("last4"),
            fingerprint=data.get("fingerprint"),
            verification_cvv=verificationCvv[verification.get("cvv").upper()],
            verification_avs=verificationAvs[verification.get("avs").upper()],
            phonenumber=metadata.get("phoneNumber"),
            email=metadata.get("email"),
            name=billing_details.get("name"),
            address_line_1=billing_details.get("line1"),
            address_line_2=billing_details.get("line2"),
            postal_code=billing_details.get("postalCode"),
            city=billing_details.get("city"),
            district=billing_details.get("district"),
            country_code=billing_details.get("country"),
            user=info.context.user,
        )

        return cls(payment_method=payment_method)
