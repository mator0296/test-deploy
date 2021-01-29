import graphene

from .mutations import CreateOrder


class OrderMutations(graphene.ObjectType):
    create_order = CreateOrder.Field()
