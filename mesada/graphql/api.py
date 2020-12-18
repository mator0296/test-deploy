import graphene

from .account.schema import AccountMutations, AccountQueries
from .core.schema import CoreMutations, CoreQueries


class Queries(AccountQueries, CoreQueries):
    node = graphene.Node.Field()


class Mutations(AccountMutations, CoreMutations):
    pass


schema = graphene.Schema(Queries, Mutations)
