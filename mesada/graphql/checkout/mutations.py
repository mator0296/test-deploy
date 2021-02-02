import graphene
from django.core.exceptions import ValidationError
from djmoney.money import Money
from graphql.error import GraphQLError

from ...account.models import Recipient
from ...checkout.models import Checkout
from ...core.utils import generate_idempotency_key
from ...payment.models import PaymentMethods
from ..core.mutations import ModelMutation
from ..core.types import Error
from .types import Checkout as CheckoutType

from mesada.checkout import CheckoutStatus
from mesada.checkout.utils import calculate_fees, galactus_call


class CheckoutInput(graphene.InputObjectType):
    amount = graphene.Decimal(description="Initial payment amount")
    fees = graphene.Decimal(description="Circle plus Mesada commission fees")
    total_amount = graphene.Decimal(description="Payment amount minus fees")
    recipient_amount = graphene.Decimal(description="Converted payment amount")
    recipient = graphene.ID(description="ID of the payment's recipient")
    payment_method = graphene.ID(description="ID of the corresponding PaymentMethod")


class CalculateOrderAmountInput(graphene.InputObjectType):
    initial_amount = graphene.Decimal(
        description="Initial amount to process", required=True
    )
    payment_method = graphene.ID(description="Payment method ID", required=True)


class CheckoutCreate(ModelMutation):
    checkout = graphene.Field(CheckoutType)

    class Arguments:
        input = CheckoutInput(required=True)

    class Meta:
        description = "Create a new Checkout"
        model = Checkout

    @classmethod
    def perform_mutation(cls, _root, info, input):
        try:
            checkout = Checkout.objects.get(user_id=info.context.user.id)

        except Checkout.DoesNotExist:
            checkout_token = generate_idempotency_key()

            try:
                recipient = Recipient.objects.get(pk=input.get("recipient"))
                payment_method = PaymentMethods.objects.get(
                    pk=input.get("payment_method")
                )
            except Recipient.DoesNotExist:
                raise ValidationError({"recipient": "Recipient not found."})
            except PaymentMethods.DoesNotExist:
                raise ValidationError({"payment_method": "Payment Method not found"})

            data = {
                "checkout_token": checkout_token,
                "amount": input.get("amount"),
                "fees": input.get("fees"),
                "total_amount": input.get("total_amount"),
                "recipient_amount": input.get("recipient_amount"),
                "user": info.context.user,
                "recipient": recipient,
                "payment_method": payment_method,
                "status": CheckoutStatus.PENDING,
                "active": True,
            }
            checkout = Checkout.objects.create(**data)

        except Checkout.MultipleObjectsReturned as e:
            raise GraphQLError(f"Internal Server Error:: {e}")

        return cls(checkout=checkout)


class CheckoutUpdate(ModelMutation):
    checkout = graphene.Field(CheckoutType)

    class Arguments:
        input = CheckoutInput(required=True)

    class Meta:
        description = "Update a previous checkout"
        model = Checkout

    @classmethod
    def perform_mutation(cls, _root, info, input):
        new_values = {key: value for key, value in input.items() if value is not None}
        checkout_qs = Checkout.objects.filter(user_id=info.context.user.id, active=True)
        checkout = checkout_qs.first()
        if checkout is None:
            error_msg = "Internal Server Error: To-be updated Checkout not found."
            raise GraphQLError(error_msg)

        if "recipient" in new_values:
            try:
                new_recipient = Recipient.objects.get(pk=new_values["recipient"])
            except Recipient.DoesNotExist:
                raise ValidationError({"recipient": "Recipient not found."})
            new_values["recipient"] = new_recipient
        if "payment_method" in new_values:
            try:
                new_payment_method = PaymentMethods.objects.get(
                    pk=new_values["payment_method"]
                )
            except PaymentMethods.DoesNotExist:
                raise ValidationError({"payment_method": "Payment Method not found."})
            new_values["payment_method"] = new_payment_method

        checkout_qs.update(**new_values)
        checkout.refresh_from_db()

        return cls(checkout=checkout)


class CalculateOrderAmount(ModelMutation):
    amount_to_convert = graphene.String(description="Payment amount to convert")
    fees_amount = graphene.String(description="Circle transaction fee")
    mesada_fee_amount = graphene.String(description="Mesada transaction fee")
    total_amount = graphene.String(description="Total amount after conversion")
    block_amount = graphene.Boolean(
        description="Denotes if the amount has been blocked"
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
        payment_method_id = input.get("payment_method")
        try:
            payment_method = PaymentMethods.objects.get(pk=payment_method_id)

        except PaymentMethods.DoesNotExist as e:
            return cls(errors=[Error(message=e)])

        amount_minus_fees, circle_fee, mesada_fee = calculate_fees(
            initial_amount, payment_method.type
        )

        if info.context.user.is_authenticated:
            # Check if a checkout already exists for this user.
            block_amount = True
            try:
                checkout, created = Checkout.objects.get_or_create(
                    user_id=info.context.user.id,
                    active=True,
                    defaults={
                        "checkout_token": generate_idempotency_key(),
                        "amount": Money(0.0, "USD"),
                        "fees": Money(0.0, "USD"),
                        "total_amount": Money(0.0, "USD"),
                        "recipient_amount": Money(0.0, "MXN"),
                    },
                )
            except Checkout.MultipleObjectsReturned as e:
                raise GraphQLError(f"Internal Server Error:: {e}")

            converted_amount = galactus_call(
                str(amount_minus_fees), block_amount, checkout.checkout_token
            )

            checkout.amount = Money(initial_amount, "USD")
            checkout.fees = Money(circle_fee + mesada_fee, "USD")
            checkout.total_amount = Money(amount_minus_fees, "USD")
            checkout.recipient_amount = Money(converted_amount, "MXN")
            checkout.payment_method = payment_method
            checkout.save(
                update_fields=[
                    "amount",
                    "fees",
                    "total_amount",
                    "recipient_amount",
                    "payment_method",
                ]
            )
            """
            try:
                checkout = Checkout.objects.get(user_id=info.context.user.id)
                converted_amount = galactus_call(
                    str(amount_minus_fees), block_amount, checkout.checkout_token
                )
                checkout.amount = Money(initial_amount, "USD")
                checkout.fees = Money(circle_fee + mesada_fee, "USD")
                checkout.total_amount = Money(amount_minus_fees, "USD")
                checkout.recipient_amount = Money(converted_amount, "MXN")
                checkout.payment_method = payment_method
                checkout.save(
                    update_fields=[
                        "amount",
                        "fees",
                        "total_amount",
                        "recipient_amount",
                        "payment_method",
                    ]
                )

            except Checkout.DoesNotExist:
                checkout_token = generate_idempotency_key()
                converted_amount = galactus_call(
                    str(amount_minus_fees), block_amount, checkout_token
                )
                data = {
                    "checkout_token": checkout_token,
                    "amount": Money(initial_amount, "USD"),
                    "fees": Money(circle_fee + mesada_fee, "USD"),
                    "total_amount": Money(amount_minus_fees, "USD"),
                    "recipient_amount": Money(converted_amount, "MXN"),
                    "user": info.context.user,
                    "payment_method": payment_method,
                }
                checkout = Checkout.objects.create(**data)
            """
        else:
            block_amount = False
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
