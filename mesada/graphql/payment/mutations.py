import graphene

from ...core.utils import generate_idempotency_key
from ...payment import create_card, processor_token_create
from ...payment.models import paymentMethods, verificationAvs, verificationCvv
from ..core.mutations import ModelMutation, BaseMutation
from .types import BillingDetailsInput, PaymentMethod
from .utils import get_default_billing_details, hash_session_id
from ...payment import request_encryption_key


class CardInput(graphene.InputObjectType):
    encrypted_data = graphene.String(description="Card encrypted data", required=True)
    key_id = graphene.String(description="Encryption key", required=True)
    exp_month = graphene.Int(description="Card expiration month", required=True)
    exp_year = graphene.Int(description="Card expiration year", required=True)
    billing_details = BillingDetailsInput(description="Card billing details")


class CreateCard(ModelMutation):
    """Create card within the Circle API and insert into the DB."""

    payment_method = graphene.Field(PaymentMethod)

    class Meta:
        description = "Save a new card withing the Circle API."
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
            payment_method_token=response.get("id"),
            user=info.context.user,
        )

        return cls(payment_method=payment_method)


class CreatePublicKey(BaseMutation):
    """
    The key retrieved is an RSA public key that needs to be b64 decoded
    to get the actual PGP public key.
    """

    key_id = graphene.String(description="Unique identifier for the public key")
    public_key = graphene.String(description="A PGP ascii-armor encoded public key")

    class Meta:
        description = "Request for a public encryption key from the Circle API."

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        key_id, public_key = request_encryption_key()
        return cls(key_id=key_id, public_key=public_key)


class ProcessorTokenInput(graphene.InputObjectType):
    public_token = graphene.String(description="Plaid public token", required=True)
    accounts = graphene.List(
        graphene.JSONString, description="List of client's accounts", required=True
    )


class ProcessorTokenCreate(ModelMutation):
    """Exchange a Plaid public token for a Circle processor token."""

    payment_method = graphene.Field(PaymentMethod)
    error = graphene.String(description="Plaid error code")
    message = graphene.String(description="Plaid error user friendly message")

    class Arguments:
        input = ProcessorTokenInput(
            description="Fields required to create a processor token.", required=True
        )

    class Meta:
        description = "Creates a new processor token."
        model = paymentMethods

    @classmethod
    def perform_mutation(cls, _root, info, input):
        access_token = input.get("public_token")
        account_id = input.get("accounts")[0]["account_id"]

        processor_token, error, message = processor_token_create(
            access_token, account_id
        )

        if processor_token is not None:
            payment_method = paymentMethods.objects.create(
                type="ACH", processor_token=processor_token, user=info.context.user
            )
            return cls(payment_method=payment_method, error=None, message=None)

        return cls(payment_method=None, error=error, message=message)
