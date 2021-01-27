import graphene
from mutations import CalculateOrderAmount


class CheckoutMutations(graphene.ObjectType):
    calculate_order_amount = CalculateOrderAmount.Field()
