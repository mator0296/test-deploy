import graphene

from ...core.utils import generate_idempotency_key
from ...payment import create_card, create_link_token
from ...payment.models import paymentMethods, verificationAvs, verificationCvv
from ..core.mutations import BaseMutation, ModelMutation
from .types import BillingDetailsInput, PaymentMethod
from .utils import get_default_billing_details, hash_session_id


class CardInput(graphene.InputObjectType):
    encrypted_data = graphene.String(
        description="Card encrypted data", required=True
    )
    key_id = graphene.String(description="Encryption key", required=True)
    exp_month = graphene.Int(
        description="Card expiration month", required=True
    )
    exp_year = graphene.Int(description="Card expiration year", required=True)
    billing_details = BillingDetailsInput(description="Card billing details")


class CreateCard(ModelMutation):
    """Create card within the Circle API and insert into the DB."""

    payment_method = graphene.Field(PaymentMethod)

    class Meta:
        description = "Save a new card within the Circle API."
        model = paymentMethods

    class Arguments:
        input = CardInput(description="Card input", required=True)

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        """Perform the card creation and insert the model into  the DB.

        Returns:
            payment_method: Instance of the model.
        """
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
            "expMonth": card.get("exp_month"),
            "expYear": card.get("exp_year"),
            "metadata": {
                "email": info.context.user.email,
                "phoneNumber": str(info.context.user.phone),
                "sessionId": hashed_session_id,
                "ipAddress": ip_address,
            },
        }

        response = create_card(body)

        billing_details = response.get("billingDetails")
        verification = response.get("verification")
        metadata = response.get("metadata")

        payment_method = paymentMethods.objects.create(
            type="CARD",
            exp_month=response.get("expMonth"),
            exp_year=response.get("expYear"),
            network=response.get("network"),
            last_digits=response.get("last4"),
            fingerprint=response.get("fingerprint"),
            verification_cvv=verificationCvv[verification.get("cvv").upper()],
            verification_avs=verificationAvs[verification.get("avs").upper()],
            phonenumber=metadata.get("phoneNumber"),
            email=metadata.get("email"),
            name=billing_details.get("name"),
            address_line_1=billing_details.get("line1"),
            address_line_2=billing_details.get("line2")
            if billing_details.get("line2")
            else "",
            postal_code=billing_details.get("postalCode"),
            city=billing_details.get("city"),
            district=billing_details.get("district"),
            country_code=billing_details.get("country"),
            payment_token=response.get("id"),
            user=info.context.user,
        )

        return cls(payment_method=payment_method)


class CreateLinkToken(BaseMutation):
    """Request a link token from the Plaid API."""

    expiration = graphene.String()
    link_token = graphene.String()
    request_id = graphene.String()

    class Meta:
        description = "Request a link token."

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        body = {
            "client_name": "Mesada",
            "country_codes": ["US"],
            "language": "en",
            "user": {
                "client_user_id": str(info.context.user.id),
                "legal_name": f"{info.context.user.first_name} {info.context.user.last_name}",
                "phone_number": str(info.context.user.phone),
                "email_address": info.context.user.email,
            },
            "products": ["auth"],
        }

        response = create_link_token(body)

        return CreateLinkToken(
            expiration=response.get("expiration"),
            link_token=response.get("link_token"),
            request_id=response.get("request_id"),
        )
