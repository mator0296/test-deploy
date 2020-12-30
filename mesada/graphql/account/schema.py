import graphene
from graphql_jwt.decorators import permission_required

from ..core.auth import login_required
from ..core.fields import FilterInputConnectionField
from ..core.types import FilterInputObjectType
from .filters import CustomerFilter, StaffUserFilter
from .mutations import (
    AddressCreate,
    AddressDelete,
    AddressUpdate,
    ChangePassword,
    CustomerCreate,
    CustomerDelete,
    CustomerPasswordReset,
    CustomerRegister,
    CustomerUpdate,
    LoggedUserUpdate,
    PasswordReset,
    SetNewPassword,
    SetPassword,
    StaffCreate,
    StaffDelete,
    StaffUpdate,
)
from .resolvers import resolve_address_validator, resolve_customers, resolve_staff_users
from .types import AddressValidationData, User


class CustomerFilterInput(FilterInputObjectType):
    class Meta:
        filterset_class = CustomerFilter


class StaffUserInput(FilterInputObjectType):
    class Meta:
        filterset_class = StaffUserFilter


class AccountQueries(graphene.ObjectType):

    customers = FilterInputConnectionField(
        User,
        filter=CustomerFilterInput(),
        description="List of the shop's customers.",
        query=graphene.String(description="Staff and Customer"),
    )
    me = graphene.Field(User, description="Logged in user data.")
    staff_users = FilterInputConnectionField(
        User,
        filter=StaffUserInput(),
        description="List of the shop's staff users.",
        query=graphene.String(description="Staff Users"),
    )
    user = graphene.Field(
        User,
        id=graphene.Argument(graphene.ID, required=True),
        description="Lookup an user by ID.",
    )

    @permission_required("account.manage_users")
    def resolve_customers(self, info, query=None, **_kwargs):
        return resolve_customers(info, query=query)

    @login_required
    def resolve_me(self, info):
        return info.context.user

    @permission_required("account.manage_staff")
    def resolve_staff_users(self, info, query=None, **_kwargs):
        return resolve_staff_users(info, query=query)

    @permission_required("account.manage_users")
    def resolve_user(self, info, id):
        return graphene.Node.get_node_from_global_id(info, id, User)


class AccountMutations(graphene.ObjectType):
    password_reset = PasswordReset.Field()
    set_password = SetPassword.Field()
    set_new_password = SetNewPassword.Field()
    change_password = ChangePassword.Field()

    customer_create = CustomerCreate.Field()
    customer_delete = CustomerDelete.Field()
    customer_password_reset = CustomerPasswordReset.Field()
    customer_register = CustomerRegister.Field()
    customer_update = CustomerUpdate.Field()

    logged_user_update = LoggedUserUpdate.Field()

    staff_create = StaffCreate.Field()
    staff_delete = StaffDelete.Field()
    staff_update = StaffUpdate.Field()

    address_create = AddressCreate.Field()
    address_delete = AddressDelete.Field()
    address_update = AddressUpdate.Field()
