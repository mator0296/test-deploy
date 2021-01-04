import graphene

from ...graphql.core.enums import to_enum
from ..core.utils import str_to_enum


class StaffMemberStatus(graphene.Enum):
    ACTIVE = "active"
    DEACTIVATED = "deactivated"


class BankName(graphene.Enum):
    BBVA = "bbva"
    BANORTE = "banorte"
    SANTANDER = "santander"
    BANAMEX = "banamex"

