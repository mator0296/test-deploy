import graphene

from ...checkout.models import Checkout as CheckoutModel
from ..core.connection import CountableDjangoObjectType


class Checkout(CountableDjangoObjectType):
    amount = graphene.String()
    fees = graphene.String()
    total_amount = graphene.String()
    recipient_amount = graphene.String()

    class Meta:
        description = "Represets a Checkout"
        interfaces = [graphene.relay.Node]
        model = CheckoutModel
        fields = "__all__"

    def resolve_amount(self, _info):
        return str(self.amount)

    def resolve_fees(self, _info):
        return str(self.fees)

    def resolve_total_amount(self, _info):
        return str(self.total_amount)

    def resolve_recipient_amount(self, _info):
        return str(self.recipient_amount)
