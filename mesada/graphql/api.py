import graphene

from .account.schema import AccountMutations, AccountQueries
from .core.schema import CoreMutations, CoreQueries
from .order.schema import OrderMutations
from .payment.schema import (
    PaymentMethodsMutations,
    PaymentMethodsQueries,
    PaymentMutations,
)


class Queries(AccountQueries, PaymentMethodsQueries, CoreQueries):
    node = graphene.Node.Field()


class Mutations(
    AccountMutations,
    CoreMutations,
    PaymentMutations,
    PaymentMethodsMutations,
    OrderMutations,
):
    pass


schema = graphene.Schema(Queries, Mutations)
