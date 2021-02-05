import graphene


class CheckoutStatusEnum(graphene.Enum):
    PENDING = "pending"
    COMPLETE = "complete"
