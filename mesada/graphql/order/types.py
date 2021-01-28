import graphene
from graphene_django.types import DjangoObjectType

from ...order.models import Order


class MoneyField(graphene.ObjectType):
    amount = graphene.Decimal()
    currency = graphene.String()

    class Meta:
        description = "Setting Money types"


class Order(DjangoObjectType):
    amount = graphene.Field(MoneyField)
    fees = graphene.Field(MoneyField)
    total_amount = graphene.Field(MoneyField)
    recipient_amount = graphene.Field(MoneyField)

    class Meta:
        description = "Create a new order"
        model = Order
        fields = "__all__"
