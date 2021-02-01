import graphene

from .account.schema import AccountMutations, AccountQueries
from .checkout.schema import CheckoutMutations
from .core.schema import CoreMutations, CoreQueries
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
    CheckoutMutations,
):
    pass


schema = graphene.Schema(Queries, Mutations)
