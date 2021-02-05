import graphene

from ...checkout.models import Checkout as CheckoutModel
from ..core.connection import CountableDjangoObjectType


class Checkout(CountableDjangoObjectType):
    amount = graphene.Decimal()
    fees = graphene.Decimal()
    total_amount = graphene.Decimal()
    recipient_amount = graphene.Decimal()

    class Meta:
        description = "Represets a Checkout"
        interfaces = [graphene.relay.Node]
        model = CheckoutModel
        fields = "__all__"

    def resolve_amount(self, _info):
        return self.amount.amount if self.amount is not None else None

    def resolve_fees(self, _info):
        return self.fees.amount if self.fees is not None else None

    def resolve_total_amount(self, _info):
        return self.total_amount.amount if self.total_amount is not None else None

    def resolve_recipient_amount(self, _info):
        return (
            self.recipient_amount.amount if self.recipient_amount is not None else None
        )
