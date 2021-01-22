import graphene
from djmoney.money import Money
from graphql.error import GraphQLError
from requests.exceptions import HTTPError

from ...core.utils import generate_idempotency_key
from ...payment.models import Payment, PaymentMethods, VerificationAvsEnum, VerificationCvvEnum
from ..core.mutations import BaseMutation, ModelMutation
from ..core.types import Error
from .types import BillingDetailsInput
from .types import Payment as PaymentType
from .types import PaymentMethod
from .utils import get_default_billing_details, hash_session_id

from mesada.payment import PaymentMethodTypes
from mesada.payment.circle import create_card, create_payment, register_ach, request_encryption_key
from mesada.payment.plaid import create_link_token, processor_token_create


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
        model = PaymentMethods

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

        payment_method = PaymentMethods.objects.create(
            type=PaymentMethodTypes.CARD,
            exp_month=response.get("expMonth"),
            exp_year=response.get("expYear"),
            network=response.get("network"),
            last_digits=response.get("last4"),
            fingerprint=response.get("fingerprint"),
            verification_cvv=VerificationCvvEnum[verification.get("cvv").upper()],
            verification_avs=VerificationAvsEnum[verification.get("avs").upper()],
            phonenumber=metadata.get("phoneNumber"),
            email=metadata.get("email"),
            name=billing_details.get("name"),
            address_line_1=billing_details.get("line1"),
            address_line_2=billing_details.get("line2", ""),
            postal_code=billing_details.get("postalCode"),
            city=billing_details.get("city"),
            district=billing_details.get("district"),
            country_code=billing_details.get("country"),
            payment_method_token=response.get("id"),
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
        response = create_link_token(info.context.user)

        return CreateLinkToken(
            expiration=response.get("expiration"),
            link_token=response.get("link_token"),
            request_id=response.get("request_id"),
        )


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


class RegisterAchPaymentInput(graphene.InputObjectType):
    public_token = graphene.String(description="Plaid public token", required=True)
    accounts = graphene.List(graphene.JSONString, description="List of client's accounts", required=True)
    billing_details = BillingDetailsInput(description="Billing details", required=True)


class RegisterAchPayment(ModelMutation):
    """Register an ACH payment in the Circle API and insert it into the DB."""

    payment_method = graphene.Field(PaymentMethod)
    errors = graphene.List(Error, required=True)

    class Arguments:
        input = RegisterAchPaymentInput(description="Fields required to create a processor token.", required=True)

    class Meta:
        description = "Creates a new processor token."
        model = PaymentMethods

    @classmethod
    def perform_mutation(cls, _root, info, input):
        public_token = input.get("public_token")
        account_id = input.get("accounts")[0]["account_id"]
        billing_details = input.get("billing_details")

        processor_token, error_msg = processor_token_create(public_token, account_id)
        if processor_token is None and error_msg is not None:
            return cls(errors=[Error(message=error_msg)])

        try:
            circle_response = register_ach(processor_token, billing_details)
            payment_method = PaymentMethods.objects.create(
                type=PaymentMethodTypes.ACH,
                payment_method_token=circle_response.get("id"),
                processor_token=processor_token,
                user=info.context.user,
                name=billing_details.get("name"),
                address_line_1=billing_details.get("line1"),
                address_line_2=billing_details.get("line2", ""),
                postal_code=billing_details.get("postalCode"),
                city=billing_details.get("city"),
                district=billing_details.get("district"),
                country_code=billing_details.get("country"),
            )
        except HTTPError as e:
            raise GraphQLError(f"Internal Server Error: {e.message}")

        return cls(payment_method=payment_method)


class CreatePayment(ModelMutation):
    """Create a payment using the Circle API."""

    payment = graphene.Field(PaymentType)

    class Arguments:
        type = graphene.String(description="Type of the transfer. Possible values are CARD or ACH.", required=True)
        payment_method = graphene.Int(description="Payment method ID.", required=True)
        amount = graphene.Float(description="Amount of the payment.", required=True)
        currency = graphene.String(description="Payment currency. Defaults to USD.", default_value="USD")
        description = graphene.String(
            description="A description of the payment to be performed. This is an optional param.",
            default_value="New Payment",
        )

    class Meta:
        description = "Create a new Payment."
        model = Payment

    @classmethod
    def perform_mutation(cls, _root, info, amount, currency, description, payment_method, type):
        if not info.context.session.session_key:
            info.context.session.save()

        ip_address = info.context.META.get("REMOTE_ADDR")
        hashed_session_id = hash_session_id(info.context.session.session_key)

        payment_method = PaymentMethods.objects.get(pk=payment_method)

        body = {
            "idempotencyKey": generate_idempotency_key(),
            "amount": {"amount": str(amount), "currency": currency},
            "source": {"id": payment_method.payment_method_token, "type": type.lower()},
            "description": description,
            "metadata": {
                "email": payment_method.email,
                "phoneNumber": payment_method.phonenumber,
                "sessionId": hashed_session_id,
                "ipAddress": ip_address,
            },
            "verification": "none",
        }

        response = create_payment(body)
        amount = response.get("amount")

        payment = Payment.objects.create(
            type=response.get("type"),
            merchant_id=response.get("merchantId"),
            merchant_wallet_id=response.get("merchantWalletId"),
            amount=Money(amount.get("amount"), amount.get("currency")),
            source=response.get("source"),
            description=response.get("description"),
            status=response.get("status"),
            metadata=response.get("metadata"),
            payment_token=response.get("id"),
            verification=response.get("verification"),
            cancel=response.get("cancel"),
            refunds=response.get("refunds"),
            fees=response.get("fees"),
            tracking_ref=response.get("trackingRef"),
            error_code=response.get("errorCode"),
            risk_evaluation=response.get("riskEvaluation"),
            user=info.context.user,
        )

        return cls(payment=payment)
