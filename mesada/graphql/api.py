import graphene

from .account.schema import AccountMutations, AccountQueries
from .checkout.schema import CheckoutMutations, CheckoutQueries
from .core.schema import CoreMutations, CoreQueries
from .payment.schema import (
    PaymentMethodsMutations,
    PaymentMethodsQueries,
    PaymentMutations,
)


class Queries(AccountQueries, PaymentMethodsQueries, CoreQueries, CheckoutQueries):
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
