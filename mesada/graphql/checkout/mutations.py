import graphene
from django.core.exceptions import ValidationError
from graphql.error import GraphQLError

from ...checkout.forms import CheckoutForm
from ...checkout.models import Checkout
from ...core.utils import generate_idempotency_key
from ...payment.models import PaymentMethods
from ..core.mutations import ModelMutation
from ..core.types import Error
from .enums import CheckoutStatusEnum
from .types import Checkout as CheckoutType

from mesada.checkout.utils import calculate_fees, galactus_call


class CheckoutCreateInput(graphene.InputObjectType):
    amount = graphene.String(description="Initial payment amount")
    fees = graphene.String(description="Circle plus Mesada commission fees")
    total_amount = graphene.String(description="Payment amount minus fees")
    recipient_amount = graphene.String(description="Converted payment amount")
    recipient = graphene.Int(description="ID of the payment's recipient")
    payment_method = graphene.Int(description="ID of the corresponding PaymentMethod")


class CheckoutUpdateInput(graphene.InputObjectType):
    amount = graphene.String(description="Initial payment amount")
    fees = graphene.String(description="Circle plus Mesada commission fees")
    total_amount = graphene.String(description="Payment amount minus fees")
    recipient_amount = graphene.String(description="Converted payment amount")
    recipient = graphene.Int(description="ID of the payment's recipient")
    payment_method = graphene.Int(description="ID of the corresponding PaymentMethod")
    status = graphene.Field(CheckoutStatusEnum)
    active = graphene.Boolean(description="Current status for the Checkout")


class CalculateOrderAmountInput(graphene.InputObjectType):
    initial_amount = graphene.String(
        description="Initial amount to process", required=True
    )
    payment_method = graphene.Int(description="Payment method ID", required=True)


class CheckoutCreate(ModelMutation):
    checkout = graphene.Field(CheckoutType)

    class Arguments:
        input = CheckoutCreateInput(required=True)

    class Meta:
        description = "Create a new Checkout"
        model = Checkout

    @classmethod
    def perform_mutation(cls, _root, info, input):
        try:
            checkout = Checkout.objects.get(user_id=info.context.user.id)

        except Checkout.DoesNotExist:
            checkout_token = generate_idempotency_key()
            data = {
                "checkout_token": checkout_token,
                **input,
                "user": info.context.user,
            }
            checkout_form = CheckoutForm(data)
            if not checkout_form.is_valid():
                raise ValidationError(checkout_form.errors)
            checkout_form.save()

        except Checkout.MultipleObjectsReturned as e:
            raise GraphQLError(f"Internal Server Error:: {e.message}")

        return cls(checkout=checkout)


class CheckoutUpdate(ModelMutation):
    checkout = graphene.Field(CheckoutType)

    class Arguments:
        input = CheckoutUpdateInput(required=True)

    class Meta:
        description = "Update a previous checkout"
        model = Checkout

    @classmethod
    def perform_mutation(cls, _root, info, input):
        try:
            checkout = Checkout.objects.get(user_id=info.context.user.id)
            checkout_form = CheckoutForm(input, instance=checkout)
            if not checkout_form.is_valid():
                raise ValidationError(checkout_form.errors)
            checkout_form.save()

        except (Checkout.DoesNotExist, Checkout.MultipleObjectsReturned) as e:
            raise GraphQLError(f"Internal Server Error:: {e.message}")

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
            return cls(errors=[Error(message=e.message)])

        amount_minus_fees, circle_fee, mesada_fee = calculate_fees(
            initial_amount, payment_method.type
        )

        if not info.context.user.is_anonymous:
            # Check if a checkout already exists for this user.
            block_amount = True
            try:
                checkout = Checkout.objects.get(user_id=info.context.user.id)
                converted_amount = galactus_call(
                    amount_minus_fees, block_amount, checkout.checkout_token
                )
                data = {
                    "amount": initial_amount,
                    "fees": circle_fee + mesada_fee,
                    "total_amount": amount_minus_fees,
                    "recipient_amount": converted_amount,
                    "payment_method": payment_method,
                }
                checkout_form = CheckoutForm(data, instance=checkout)
                if not checkout_form.is_valid():
                    raise ValidationError(checkout_form.errors)
                checkout = checkout_form.save()

            except Checkout.DoesNotExist:
                checkout_token = generate_idempotency_key()
                converted_amount = galactus_call(
                    amount_minus_fees, block_amount, checkout_token
                )
                data = {
                    "checkout_token": checkout_token,
                    "amount": initial_amount,
                    "fees": circle_fee + mesada_fee,
                    "total_amount": amount_minus_fees,
                    "recipient_amount": converted_amount,
                    "user": info.context.user,
                    "payment_method": payment_method,
                }
                checkout_form = CheckoutForm(data)
                if not checkout_form.is_valid():
                    raise ValidationError(checkout_form.errors)
                checkout = checkout_form.save()

            except Checkout.MultipleObjectsReturned as e:
                raise GraphQLError(f"Internal Server Error:: {e.message}")

            return cls(
                amount_to_convert=amount_minus_fees,
                fees_amount=circle_fee,
                mesada_fee_amount=mesada_fee,
                total_amount=converted_amount,
                block_amount=block_amount,
                checkout=checkout,
            )

        block_amount = False
        converted_amount = galactus_call(amount_minus_fees, block_amount)

        return cls(
            amount_to_convert=amount_minus_fees,
            fees_amount=circle_fee,
            mesada_fee_amount=mesada_fee,
            total_amount=converted_amount,
            block_amount=block_amount,
            checkout=None,
        )
