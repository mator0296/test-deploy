import graphene
import graphene_django_optimizer as gql_optimizer
from django.conf import settings
from django.contrib.auth import get_user_model
from graphene import relay
from graphql_jwt.decorators import permission_required

from ...account.models import Address, User
from ...core.permissions import get_permissions
from ..core.connection import CountableDjangoObjectType
from ..core.types import CountryDisplay, FilterInputObjectType, PermissionDisplay
from ..utils import format_permissions_for_display
from .filters import CustomerFilter, StaffUserFilter


class CustomerFilterInput(FilterInputObjectType):
    class Meta:
        filterset_class = CustomerFilter


class StaffUserInput(FilterInputObjectType):
    class Meta:
        filterset_class = StaffUserFilter


class AddressInput(graphene.InputObjectType):
    address_name = graphene.String(description="Address Name ID.")
    first_name = graphene.String(description="Given name.")
    last_name = graphene.String(description="Family name.")
    company_name = graphene.String(description="Company or organization.")
    street_address_1 = graphene.String(description="Address.")
    street_address_2 = graphene.String(description="Address.")
    city = graphene.String(description="City.")
    city_area = graphene.String(description="District.")
    postal_code = graphene.String(description="Postal code.")
    country = graphene.String(description="Country.")
    country_area = graphene.String(description="State or province.")


class Address(CountableDjangoObjectType):
    country = graphene.Field(
        CountryDisplay, required=True, description="Default user's country"
    )
    is_default_address = graphene.Boolean(
        required=False, description="Address is user's default address"
    )

    class Meta:
        description = "Represents user address data."
        interfaces = [relay.Node]
        model = Address
        only_fields = [
            "address_name",
            "city",
            "city_area",
            "company_name",
            "country",
            "country_area",
            "first_name",
            "id",
            "last_name",
            "postal_code",
            "street_address_1",
            "street_address_2",
        ]

    def resolve_country(self, _info):
        return CountryDisplay(code=self.country.code, country=self.country.name)

    def resolve_is_default_address(self, _info):
        """
        This field is added through annotation when using the
        `resolve_addresses` resolver.
        """
        if not hasattr(self, "user_default_address_pk"):
            return None

        user_default_address_pk = getattr(self, "user_default_address_pk")
        if user_default_address_pk == self.pk:
            return True
        return False


class User(CountableDjangoObjectType):
    addresses = gql_optimizer.field(
        graphene.List(Address, description="List of all user's addresses."),
        model_field="addresses",
    )
    note = graphene.String(description="A note about the customer")
    permissions = graphene.List(
        PermissionDisplay, description="List of user's permissions."
    )

    class Meta:
        description = "Represents user data."
        interfaces = [relay.Node]
        model = get_user_model()
        only_fields = [
            "date_joined",
            "default_address",
            "email",
            "first_name",
            "id",
            "is_active",
            "is_staff",
            "last_login",
            "last_name",
            "note",
        ]

    def resolve_addresses(self, _info, **_kwargs):
        return self.addresses.annotate_default(self).visible().order_by("-id")

    def resolve_permissions(self, _info, **_kwargs):
        if self.is_superuser:
            permissions = get_permissions()
        else:
            permissions = self.user_permissions.prefetch_related(
                "content_type"
            ).order_by("codename")
        return format_permissions_for_display(permissions)

    @permission_required("account.manage_users")
    def resolve_note(self, _info):
        return self.note


class AddressValidationData(graphene.ObjectType):
    country_code = graphene.String()
    country_name = graphene.String()
    address_format = graphene.String()
    address_latin_format = graphene.String()
    allowed_fields = graphene.List(graphene.String)
    required_fields = graphene.List(graphene.String)
    upper_fields = graphene.List(graphene.String)
    country_area_type = graphene.String()
    city_type = graphene.String()
    city_area_type = graphene.String()
    postal_code_type = graphene.String()
    postal_code_matchers = graphene.List(graphene.String)
    postal_code_examples = graphene.List(graphene.String)
    postal_code_prefix = graphene.String()
