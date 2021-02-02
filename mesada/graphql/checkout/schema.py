import graphene
from graphql.error import GraphQLError

from .mutations import CalculateOrderAmount, CheckoutCreate, CheckoutUpdate
from .types import Checkout as CheckoutType

from mesada.checkout.models import Checkout


class CheckoutQueries(graphene.ObjectType):
    checkout = graphene.Field(
        CheckoutType, description="Return the Checkout associated with the user."
    )

    def resolve_checkout(self, info):
        try:
            checkout = Checkout.objects.get(user_id=info.context.user.id)

        except Checkout.DoesNotExist as e:
            raise GraphQLError(f"Internal Server Error:: {e}")

        return checkout


class CheckoutMutations(graphene.ObjectType):
    checkout_create = CheckoutCreate.Field()
    checkout_update = CheckoutUpdate.Field()

    calculate_order_amount = CalculateOrderAmount.Field()
