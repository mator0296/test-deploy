import graphene
from djmoney.money import Money
from graphql import GraphQLError

from ...checkout.models import Checkout
from ...core.utils import generate_idempotency_key
from ...order import OrderStatus
from ...order.models import Order
from ...payment.models import Payment
from ..core.mutations import BaseMutation
from ..payment.utils import hash_session_id
from .types import Order as OrderType

from mesada.payment.circle import create_payment


class CreateOrder(BaseMutation):
    """Create a payment using the Circle API and generate a new Order."""

    order = graphene.Field(OrderType)

    class Meta:
        description = "Creates a new order."

    @classmethod
    def create_order_payment(cls, checkout, hashed_session_id, ip_address):

        body = {
            "idempotencyKey": generate_idempotency_key(),
            "amount": {
                "amount": str(checkout.amount.amount),
                "currency": str(checkout.amount.currency),
            },
            "source": {
                "id": checkout.payment_method.payment_method_token,
                "type": checkout.payment_method.type.lower(),
            },
            "description": "New Payment for checkout " + str(checkout.id),
            "metadata": {
                "email": checkout.payment_method.email,
                "phoneNumber": checkout.payment_method.phonenumber,
                "sessionId": hashed_session_id,
                "ipAddress": ip_address,
            },
            "verification": "none",
        }
        response = create_payment(body)
        return response

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        user = info.context.user.id

        try:
            checkout = Checkout.objects.get(user_id=user, active="True")
            if not info.context.session.session_key:
                info.context.session.save()

            ip_address = info.context.META.get("REMOTE_ADDR")
            hashed_session_id = hash_session_id(info.context.session.session_key)

            response = cls.create_order_payment(checkout, hashed_session_id, ip_address)
            amount = response.pop("amount")
            data = {
                "merchant_id": response.pop("merchantId"),
                "merchant_wallet_id": response.pop("merchantWalletId"),
                "amount": Money(amount.pop("amount"), amount.pop("currency")),
                "tracking_ref": response.pop("trackingRef", None),
                "error_code": response.pop("errorCode", None),
                "risk_evaluation": response.pop("riskEvaluation", None),
                "user": info.context.user,
                "payment_token": response.pop("id"),
                **response,
            }
            payment = Payment.objects.create(**data)
            order = Order.objects.create(
                checkout_id=checkout.id,
                status=OrderStatus.PENDING,
                amount=checkout.amount,
                fees=checkout.fees,
                total_amount=checkout.total_amount,
                recipient_amount=checkout.recipient_amount,
                user_id=checkout.user_id,
                recipient_id=checkout.recipient_id,
                payment_method_id=checkout.payment_method_id,
                payment_id=payment.id,
            )

            checkout.active = False
            checkout.save(update_fields=["active"])
            return cls(order=order)

        except Checkout.DoesNotExist:
            raise GraphQLError("Internal Server Error: No active checkout for user.")
        except Checkout.MultipleObjectsReturned:
            raise GraphQLError(
                "Internal Error: Found more than one active checkout for this user."
            )
