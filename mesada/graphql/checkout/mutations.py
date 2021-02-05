import graphene
from django.core.exceptions import ValidationError
from djmoney.money import Money
from graphql.error import GraphQLError

from ...account.models import Recipient
from ...checkout.models import Checkout
from ...core.utils import generate_idempotency_key
from ...payment.models import PaymentMethods
from ..core.auth import login_required
from ..core.mutations import ModelMutation
from ..core.types import Error
from .types import Checkout as CheckoutType

from mesada.checkout.utils import calculate_fees, galactus_call
from mesada.payment import PaymentMethodTypes


class CheckoutCreate(ModelMutation):
    checkout = graphene.Field(CheckoutType)

    class Meta:
        description = "Create a new Checkout"
        model = Checkout

    @classmethod
    @login_required
    def perform_mutation(cls, _root, info):
        checkout, _ = Checkout.objects.get_or_create(
            user_id=info.context.user.id,
            active=True,
            defaults={
                "checkout_token": generate_idempotency_key(),
                "user": info.context.user,
            },
        )

        return cls(checkout=checkout)


class CheckoutUpdateInput(graphene.InputObjectType):
    amount = graphene.Decimal(description="Initial payment amount", required=False)
    fees = graphene.Decimal(
        description="Circle plus Mesada commission fees", required=False
    )
    total_amount = graphene.Decimal(
        description="Payment amount minus fees", required=False
    )
    recipient_amount = graphene.Decimal(
        description="Converted payment amount", required=False
    )
    recipient = graphene.ID(description="ID of the payment's recipient", required=False)
    payment_method = graphene.ID(
        description="ID of the corresponding PaymentMethod", required=False
    )


class CheckoutUpdate(ModelMutation):
    checkout = graphene.Field(CheckoutType)

    class Arguments:
        input = CheckoutUpdateInput(required=True)

    class Meta:
        description = "Update a previous checkout"
        model = Checkout

    @classmethod
    @login_required
    def perform_mutation(cls, _root, info, input):
        new_values = {key: value for key, value in input.items() if value is not None}
        checkout_qs = Checkout.objects.filter(user_id=info.context.user.id, active=True)
        checkout = checkout_qs.first()
        if checkout is None:
            error_msg = "Internal Server Error: To-be updated Checkout not found."
            raise GraphQLError(error_msg)

        if "recipient" in new_values:
            try:
                _, recipient_id = graphene.relay.Node.from_global_id(
                    new_values["recipient"]
                )
                new_recipient = Recipient.objects.get(pk=recipient_id)
                new_values["recipient"] = new_recipient
            except Recipient.DoesNotExist:
                raise ValidationError({"recipient": "Recipient not found."})
        if "payment_method" in new_values:
            try:
                _, payment_id = graphene.relay.Node.from_global_id(
                    new_values["payment_method"]
                )
                new_payment_method = PaymentMethods.objects.get(pk=payment_id)
                new_values["payment_method"] = new_payment_method
            except PaymentMethods.DoesNotExist:
                raise ValidationError({"payment_method": "Payment Method not found."})

        checkout_qs.update(**new_values)
        checkout.refresh_from_db()

        return cls(checkout=checkout)


class CalculateOrderAmountInput(graphene.InputObjectType):
    initial_amount = graphene.Decimal(
        description="Initial amount to process", required=True
    )
    payment_method_type = graphene.Field(
        graphene.Enum.from_enum(PaymentMethodTypes),
        description="Payment method type",
        required=True,
    )
    block_amount = graphene.Boolean(
        description="Signals whenever to block or not the funds.", required=True
    )
    update_checkout = graphene.Boolean(
        description="Signals to update or not the existing checkout.", required=True
    )


class CalculateOrderAmount(ModelMutation):
    amount_to_convert = graphene.Decimal(description="Payment amount to convert")
    fees_amount = graphene.Decimal(description="Circle transaction fee")
    mesada_fee_amount = graphene.Decimal(description="Mesada transaction fee")
    total_amount = graphene.Decimal(description="Total amount after conversion")
    block_amount = graphene.Boolean(
        description="Denotes if the amount has been blocked", required=False
    )
    checkout = graphene.Field(
        CheckoutType, description="The created or updated Checkout"
    )
    errors = graphene.List(Error, required=True)

    class Arguments:
        input = CalculateOrderAmountInput(required=True)

    class Meta:
        description = "Calculate order amount and create a corresponding Checkout"
        model = Checkout

    @classmethod
    def perform_mutation(cls, _root, info, input):
        initial_amount = input.get("initial_amount")
        payment_method_type = input.get("payment_method_type")

        amount_minus_fees, circle_fee, mesada_fee = calculate_fees(
            initial_amount, payment_method_type
        )
        block_amount = input.get("block_amount")
        update_checkout = input.get("update_checkout")

        if info.context.user.is_authenticated:
            # Check if a checkout already exists for this user.
            checkout_qs = Checkout.objects.filter(
                user_id=info.context.user.id, active=True
            )
            checkout = checkout_qs.first()
            if checkout is None:
                error_msg = "Internal Server Error: User has no matching Checkout"
                raise GraphQLError(error_msg)

            if block_amount:
                converted_amount = galactus_call(
                    str(amount_minus_fees), block_amount, checkout.checkout_token
                )
            else:
                converted_amount = galactus_call(str(amount_minus_fees), block_amount)

            if update_checkout:
                data = {
                    "amount": Money(initial_amount, "USD"),
                    "fees": Money(circle_fee + mesada_fee, "USD"),
                    "total_amount": Money(amount_minus_fees, "USD"),
                    "recipient_amount": Money(converted_amount, "MXN"),
                }
                checkout_qs.update(**data)
                checkout.refresh_from_db()
        else:
            checkout = None
            converted_amount = galactus_call(amount_minus_fees, block_amount)

        return cls(
            amount_to_convert=str(amount_minus_fees),
            fees_amount=str(circle_fee),
            mesada_fee_amount=str(mesada_fee),
            total_amount=converted_amount,
            block_amount=block_amount,
            checkout=checkout,
        )
