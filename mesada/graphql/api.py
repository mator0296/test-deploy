import graphene

from .account.schema import AccountMutations, AccountQueries
from .core.schema import CoreMutations, CoreQueries
from .payment.schema import PaymentMutations


class Queries(AccountQueries, CoreQueries):
    node = graphene.Node.Field()


class Mutations(AccountMutations, CoreMutations, PaymentMutations):
    pass


schema = graphene.Schema(Queries, Mutations)
