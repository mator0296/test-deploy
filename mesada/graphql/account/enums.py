import graphene


class StaffMemberStatus(graphene.Enum):
    ACTIVE = "active"
    DEACTIVATED = "deactivated"


class ValidatePhoneStatusEnum(graphene.Enum):
    PROCEED = 1
    REJECTED = 2
    APPROVED = 3


class BankName(graphene.Enum):
    BBVA = "bbva"
    BANORTE = "banorte"
    SANTANDER = "santander"
    BANAMEX = "banamex"
