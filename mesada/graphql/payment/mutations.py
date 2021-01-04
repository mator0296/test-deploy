import graphene
import hashlib

from ...core.utils import generate_idempotency_key
from ...payment import create_card
from ...payment.models import paymentMethods, verificationAvs, verificationCvv
from ..core.mutations import ModelMutation
from .types import BillingDetailsInput, PaymentMethod


def hash_session_id(session_id):
    return hashlib.md5(session_id.encode("utf-8")).hexdigest()


class CardInput(graphene.InputObjectType):
    encrypted_data = graphene.String(description="Card encrypted data", required=True)
    key_id = graphene.String(description="Encryption key", required=True)
    exp_month = graphene.Int(description="Card expiration month", required=True)
    exp_year = graphene.Int(description="Card expiration year", required=True)
    billing_details = BillingDetailsInput(description="Card billing details")


class CreateCard(ModelMutation):
    response = graphene.JSONString()
    payment_method = graphene.Field(PaymentMethod)

    class Meta:
        description = "Save a new card withing the Circle API."
        model = paymentMethods

    class Arguments:
        input = CardInput(description="Card input", required=True)

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        default_address = info.context.user.default_address
        card = data.get("input")
        billing_details = card.get("billing_details")
        if not billing_details:
            billing_details = {
                "name": f"{default_address.first_name} {default_address.last_name}",
                "city": default_address.city,
                "country": str(default_address.country),
                "line1": default_address.street_address_1,
                "line2": default_address.street_address_2,
                "district": default_address.country_area,
                "postalCode": default_address.postal_code,
            }
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
        print(response.status_code)
        data = response.json().get("data")
        """ data = {
            "id": "1e38dcef-a947-493a-a674-f623e4418ace",
            "billingDetails": {
                "name": "Satoshi Nakamoto",
                "city": "Boston",
                "country": "US",
                "line1": "100 Money Street",
                "line2": "Suite 1",
                "district": "MA",
                "postalCode": "01234",
            },
            "expMonth": 1,
            "expYear": 2020,
            "network": "VISA",
            "last4": "0123",
            "fingerprint": "eb170539-9e1c-4e92-bf4f-1d09534fdca2",
            "errorCode": "verification_failed",
            "verification": {"avs": "O", "cvv": "not_requested"},
            "riskEvaluation": {"decision": "denied", "reason": "3000"},
            "metadata": {"email": "satoshi@circle.com", "phoneNumber": "+14155555555"},
            "createDate": "2019-09-18T19:19:01Z",
            "updateDate": "2019-09-18T19:20:00Z",
        } """

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

        return cls(response=response.json(), payment_method=payment_method)
