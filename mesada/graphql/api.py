import graphene

from .account.schema import AccountMutations, AccountQueries
from .core.schema import CoreMutations, CoreQueries
from .payment.schema import (
    PaymentMethodsMutations,
    PaymentMethodsQueries,
    PaymentMutations,
)
from .order.schema import OrderMutations


class Queries(AccountQueries, PaymentMethodsQueries, CoreQueries):
    node = graphene.Node.Field()


class Mutations(
    AccountMutations, CoreMutations, PaymentMutations, PaymentMethodsMutations, OrderMutations
):
    pass


schema = graphene.Schema(Queries, Mutations)
