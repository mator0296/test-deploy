import graphene

from ..core.mutations import BaseMutation


class CardInput(graphene.InputObjectType):
    encrypted_data = graphene.String(description="Card encrypted data")
    key_id = graphene.String(description="Encryption key")
    exp_month = graphene.String(description="Card expiration month")
    exp_year = graphene.String(description="Card expiration year")


class CreateCard(BaseMutation):
    class Arguments:
        input = CardInput(description="Card input", required=True)

    class Meta:
        description = "Save a new card withing the Circle API."

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        ip_address = info.context.META.get("REMOTE_ADDR")
        session = info.context.META.session
        print(ip_address)
        print(str(session))
        return ip_address
