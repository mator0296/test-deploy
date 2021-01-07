import graphene
from graphql_jwt.decorators import permission_required

from ..core.auth import login_required
from ..core.fields import FilterInputConnectionField
from ..core.types import FilterInputObjectType
from .filters import AddressFilter, CustomerFilter, StaffUserFilter
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
    RecipientCreate,
    RecipientUpdate,
    RecipientDelete,
    SendPhoneVerificationSMS,
    SetNewPassword,
    SetPassword,
    StaffCreate,
    StaffDelete,
    StaffUpdate,
    VerifySMSCodeVerification,
)
from .resolvers import (
    resolve_address,
    resolve_address_validator,
    resolve_addresses,
    resolve_customers,
    resolve_staff_users,
)


from .types import Address, AddressValidationData, User


class CustomerFilterInput(FilterInputObjectType):
    class Meta:
        filterset_class = CustomerFilter


class StaffUserInput(FilterInputObjectType):
    class Meta:
        filterset_class = StaffUserFilter


class AddressFilterInput(FilterInputObjectType):
    class Meta:
        filterset_class = AddressFilter


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
    address = graphene.Field(
        Address,
        id=graphene.Argument(graphene.ID, required=True),
        description="Lookup an address by ID.",
    )
    addresses = FilterInputConnectionField(
        Address,
        filter=AddressFilterInput(),
        description="List of addresses.",
        search=graphene.String(description="Address lookup string"),
        query=graphene.String(description="Addresses"),
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

    def resolve_address(self, info, id):
        return resolve_address(info, id)

    def resolve_addresses(self, info, search, query=None, **_kwargs):
        return resolve_addresses(info, search=search, query=query)


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

    recipient_create = RecipientCreate.Field()
    recipient_update = RecipientUpdate.Field()
    recipient_delete = RecipientDelete.Field()

    sendPhoneVerificationSMS = SendPhoneVerificationSMS.Field()
    verifySMSCodeVerification = VerifySMSCodeVerification.Field()
