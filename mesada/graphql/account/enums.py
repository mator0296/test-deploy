import graphene

from ...graphql.core.enums import to_enum
from ..core.utils import str_to_enum


class StaffMemberStatus(graphene.Enum):
    ACTIVE = "active"
    DEACTIVATED = "deactivated"


class EnumStatus(graphene.Enum):
    proceed = 1
    rejected = 2
    approved = 3
