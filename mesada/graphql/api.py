import graphene

from .account.schema import AccountMutations, AccountQueries
from .core.schema import CoreMutations, CoreQueries
from .payment.schema import (
    PaymentMutations,
    PaymentMethodsMutations,
    PaymentMethodsQueries,
)


class Queries(AccountQueries, PaymentMethodsQueries, CoreQueries):
    node = graphene.Node.Field()


class Mutations(
    AccountMutations, CoreMutations, PaymentMutations, PaymentMethodsMutations
):
    pass


schema = graphene.Schema(Queries, Mutations)
