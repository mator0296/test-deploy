import graphene
from graphql.error import GraphQLError

from ...checkout.models import Checkout
from ...core.utils import generate_idempotency_key
from ...payment.models import PaymentMethods
from ..core.mutations import ModelMutation
from ..core.types import Error

from mesada.checkout.utils import calculate_fees, get_amount


class CalculateOrderAmountInput(graphene.InputObjectType):
    initial_amount = graphene.String(
        description="Initial amount to process", required=True
    )
    payment_method = graphene.Int(description="Payment method ID", required=True)


class CalculateOrderAmount(ModelMutation):
    amount_to_convert = graphene.String(description="Payment amount to convert")
    fees_amount = graphene.String(description="Circle transaction fee")
    mesada_fee_amount = graphene.String(description="Mesada transaction fee")
    errors = graphene.List(Error, required=True)

    class Meta:
        description = "Calculate order amount and create a corresponding Checkout"
        model = Checkout

    @classmethod
    def perform_mutation(cls, _root, info, initial_amount, payment_method_id):
        try:
            payment_method = PaymentMethods.objects.get(pk=payment_method_id)

        except PaymentMethods.DoesNotExist as e:
            return cls(errors=[Error(message=e.message)])

        amount_minus_fees, circle_fee, mesada_fee = calculate_fees(
            initial_amount, payment_method.type
        )

        # Check if a checkout already exists for this user.
        try:
            # checkout = Checkout.objects.get(user_id=info.content.user.id)
            # Galactus endpoint call.
            body = {"amount_to_convert": amount_minus_fees, "block_amount": True}
            galactus_response = get_amount(body)
            amount_to_convert = galactus_response["amount"]

        except Checkout.DoesNotExist:
            checkout_token = generate_idempotency_key()
            # Galactus endpoint call.
            body = {
                "amount_to_convert": amount_minus_fees,
                "block_amount": True,
                "checkout_token": checkout_token,
            }
            galactus_response = get_amount(body)
            amount_to_convert = galactus_response["amount"]

            # checkout = Checkout.objects.create(
            #     checkout_token=checkout_token,
            #     total_amount=initial_amount,
            #     user=info.context.user,
            #     payment_method=payment_method,
            # )

        except Checkout.MultipleObjectsReturned as e:
            raise GraphQLError(f"Internal Server Error:: {e.message}")

        return cls(
            amount_to_convert=amount_to_convert,
            fees_amount=circle_fee,
            mesada_fee_amount=mesada_fee,
        )
