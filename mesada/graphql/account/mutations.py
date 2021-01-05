from copy import copy

import graphene
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import IntegrityError
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from graphql_jwt.decorators import staff_member_required
from graphql_jwt.exceptions import PermissionDenied
from graphql_jwt.shortcuts import get_token
from twilio.base.exceptions import TwilioRestException

from graphql.error import GraphQLError

from ...account import models
from ...core.permissions import get_permissions
from ...core.twilio import send_code, check_code
from ..account.types import Address, AddressInput, User, Recipient, RecipientInput
from ..core.enums import PermissionEnum
from ..core.mutations import BaseMutation, ModelDeleteMutation, ModelMutation
from ..core.types import Upload
from ..core.utils import get_user_instance
from .enums import ValidatePhoneStatusEnum
from .utils import CustomerDeleteMixin, StaffDeleteMixin, UserDeleteMixin

ADDRESS_FIELD = "billing_address"


def send_user_password_reset_email(user, site):
    context = {
        "email": user.email,
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": default_token_generator.make_token(user),
        "site_name": site.name,
        "domain": site.domain,
        "protocol": "https" if settings.ENABLE_SSL else "http",
    }


def can_edit_address(user, address, check_user_permission=True):
    """Determine whether the user can edit the given address.

    This method assumes that an address can be edited by:
    - users with proper permission (staff)
    - customers who "own" the given address.
    """
    belongs_to_user = address in user.addresses.all()
    if check_user_permission:
        has_perm = user.has_perm("account.manage_users")
        return has_perm or belongs_to_user
    return belongs_to_user


class CustomerRegisterInput(graphene.InputObjectType):
    first_name = graphene.String(description="First Name")
    last_name = graphene.String(description="Last Name")
    email = graphene.String(
        description="The unique email address of the user.", required=True
    )
    password = graphene.String(description="Password", required=True)
    phone = graphene.String(description="Phone Number", required=True)


class CustomerRegister(ModelMutation):
    token = graphene.String()

    class Arguments:
        input = CustomerRegisterInput(
            description="Fields required to create a user.", required=True
        )

    class Meta:
        description = "Register a new user."
        exclude = ["password", "postal_code"]
        model = models.User

    @classmethod
    def clean_input(cls, info, instance, data):
        cleaned_input = super().clean_input(info, instance, data)
        return cleaned_input

    @classmethod
    def save(cls, info, user, cleaned_input):
        password = cleaned_input["password"]
        user.set_password(password)
        user.save()
        return user

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        success_response = super().perform_mutation(_root, info, **data)
        user = success_response.user
        token = get_token(user, info.context)
        setattr(success_response, "token", token)
        return success_response


class UserInput(graphene.InputObjectType):
    first_name = graphene.String(description="Given name.")
    last_name = graphene.String(description="Family name.")
    email = graphene.String(description="The unique email address of the user.")
    is_active = graphene.Boolean(required=False, description="User account is active.")
    note = graphene.String(description="A note about the user.")


class UserAddressInput(graphene.InputObjectType):
    default_address = AddressInput(description="address of the customer.")


class CustomerInput(UserInput, UserAddressInput):
    pass


class UserCreateInput(CustomerInput):
    send_password_email = graphene.Boolean(
        description="Send an email with a link to set a password"
    )


class StaffInput(UserInput):
    permissions = graphene.List(
        PermissionEnum,
        description="List of permission code names to assign to this user.",
    )


class StaffCreateInput(StaffInput):
    send_password_email = graphene.Boolean(
        description="Send an email with a link to set a password"
    )


class CustomerCreate(ModelMutation):
    class Arguments:
        input = UserCreateInput(
            description="Fields required to create a customer.", required=True
        )

    class Meta:
        description = "Creates a new customer."
        exclude = ["password"]
        model = models.User
        permissions = ("account.manage_users",)

    @classmethod
    def clean_input(cls, info, instance, data):
        address_data = data.pop(ADDRESS_FIELD, None)
        cleaned_input = super().clean_input(info, instance, data)

        if address_data:
            shipping_address = cls.validate_address(
                address_data, instance=getattr(instance, ADDRESS_FIELD)
            )
            cleaned_input[ADDRESS_FIELD] = address_data

        return cleaned_input

    @classmethod
    def save(cls, info, instance, cleaned_input):
        # FIXME: save address in user.addresses as well
        address_data = cleaned_input.get(ADDRESS_FIELD)
        if address_data:
            address_data.save()
            instance.default_shipping_address = address_data
        address_data = cleaned_input.get(ADDRESS_FIELD)
        if address_data:
            address_data.save()
            instance.address_data = address_data

        is_creation = instance.pk is None
        super().save(info, instance, cleaned_input)


class CustomerUpdate(CustomerCreate):
    class Arguments:
        id = graphene.ID(description="ID of a customer to update.", required=True)
        input = CustomerInput(
            description="Fields required to update a customer.", required=True
        )

    class Meta:
        description = "Updates an existing customer."
        exclude = ["password"]
        model = models.User
        permissions = ("account.manage_users",)

    @classmethod
    def generate_events(
        cls, info, old_instance: models.User, new_instance: models.User
    ):
        # Retrieve the event base data
        staff_user = info.context.user
        new_email = new_instance.email
        new_fullname = new_instance.get_full_name()

        # Compare the data
        has_new_name = old_instance.get_full_name() != new_fullname
        has_new_email = old_instance.email != new_email

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        """Override the base method `perform_mutation` of ModelMutation
        to generate events by comparing the old instance with the new data."""

        # Retrieve the data
        original_instance = cls.get_instance(info, **data)
        data = data.get("input")

        # Clean the input and generate a new instance from the new data
        cleaned_input = cls.clean_input(info, original_instance, data)
        new_instance = cls.construct_instance(copy(original_instance), cleaned_input)

        # Save the new instance data
        cls.clean_instance(new_instance)
        cls.save(info, new_instance, cleaned_input)
        cls._save_m2m(info, new_instance, cleaned_input)

        # Generate events by comparing the instances
        cls.generate_events(info, original_instance, new_instance)

        # Return the response
        return cls.success_response(new_instance)


class LoggedUserUpdate(CustomerCreate):
    class Arguments:
        input = CustomerInput(
            description="Fields required to update logged in user.", required=True
        )

    class Meta:
        description = "Updates data of the logged in user."
        exclude = ["password"]
        model = models.User

    @classmethod
    def check_permissions(cls, user):
        return user.is_authenticated

    @classmethod
    def perform_mutation(cls, root, info, **data):
        user = info.context.user
        data["id"] = graphene.Node.to_global_id("User", user.id)
        return super().perform_mutation(root, info, **data)


class UserDelete(UserDeleteMixin, ModelDeleteMutation):
    class Meta:
        abstract = True


class CustomerDelete(CustomerDeleteMixin, UserDelete):
    class Meta:
        description = "Deletes a customer."
        model = models.User
        permissions = ("account.manage_users",)

    class Arguments:
        id = graphene.ID(required=True, description="ID of a customer to delete.")

    @classmethod
    def perform_mutation(cls, root, info, **data):
        results = super().perform_mutation(root, info, **data)
        cls.post_process(info)
        return results


class StaffCreate(ModelMutation):
    class Arguments:
        input = StaffCreateInput(
            description="Fields required to create a staff user.", required=True
        )

    class Meta:
        description = "Creates a new staff user."
        exclude = ["password", "postal_code"]
        model = models.User
        permissions = ("account.manage_staff",)

    @classmethod
    def clean_input(cls, info, instance, data):
        import pdb

        pdb.set_trace()
        cleaned_input = super().clean_input(info, instance, data)

        # set is_staff to True to create a staff user
        cleaned_input["is_staff"] = True

        # clean and prepare permissions
        if "permissions" in cleaned_input:
            permissions = cleaned_input.pop("permissions")
            cleaned_input["user_permissions"] = get_permissions(permissions)
        return cleaned_input

    @classmethod
    def save(cls, info, user, cleaned_input):
        user.save()


class StaffUpdate(StaffCreate):
    class Arguments:
        id = graphene.ID(description="ID of a staff user to update.", required=True)
        input = StaffInput(
            description="Fields required to update a staff user.", required=True
        )

    class Meta:
        description = "Updates an existing staff user."
        exclude = ["password"]
        model = models.User
        permissions = ("account.manage_staff",)

    @classmethod
    def clean_is_active(cls, is_active, instance, user):
        if not is_active:
            if user == instance:
                raise ValidationError(
                    {"is_active": "Cannot deactivate your own account."}
                )
            elif instance.is_superuser:
                raise ValidationError(
                    {"is_active": "Cannot deactivate superuser's account."}
                )

    @classmethod
    def clean_input(cls, info, instance, data):
        cleaned_input = super().clean_input(info, instance, data)
        is_active = cleaned_input.get("is_active")
        if is_active is not None:
            cls.clean_is_active(is_active, instance, info.context.user)
        return cleaned_input


class StaffDelete(StaffDeleteMixin, UserDelete):
    class Meta:
        description = "Deletes a staff user."
        model = models.User
        permissions = ("account.manage_staff",)

    class Arguments:
        id = graphene.ID(required=True, description="ID of a staff user to delete.")

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        if not cls.check_permissions(info.context.user):
            raise PermissionDenied()

        user_id = data.get("id")
        instance = cls.get_node_or_error(info, user_id, only_type=User)
        cls.clean_instance(info, instance)

        db_id = instance.id
        # After the instance is deleted, set its ID to the original database's
        # ID so that the success response contains ID of the deleted object.
        instance.id = db_id
        return cls.success_response(instance)


class SetPasswordInput(graphene.InputObjectType):
    token = graphene.String(
        description="A one-time token required to set the password.", required=True
    )
    password = graphene.String(description="Password", required=True)


class SetPassword(ModelMutation):
    INVALID_TOKEN = "Invalid or expired token."

    class Arguments:
        id = graphene.ID(
            description="ID of a user to set password whom.", required=True
        )
        input = SetPasswordInput(
            description="Fields required to set password.", required=True
        )

    class Meta:
        description = "Sets user password."
        model = models.User

    @classmethod
    def clean_input(cls, info, instance, data):
        cleaned_input = super().clean_input(info, instance, data)
        token = cleaned_input.pop("token")
        if not default_token_generator.check_token(instance, token):
            raise ValidationError({"token": SetPassword.INVALID_TOKEN})
        return cleaned_input

    @classmethod
    def save(cls, info, instance, cleaned_input):
        instance.set_password(cleaned_input["password"])
        instance.save()


class PasswordReset(BaseMutation):
    class Arguments:
        email = graphene.String(description="Email", required=True)

    class Meta:
        description = "Sends password reset email"
        permissions = ("account.manage_users",)

    @classmethod
    def perform_mutation(cls, _root, info, email):
        try:
            user = models.User.objects.get(email=email)
        except ObjectDoesNotExist:
            raise ValidationError({"email": "User with this email doesn't exist"})
        site = info.context.site
        send_user_password_reset_email(user, site)
        return PasswordReset()


class CustomerPasswordResetInput(graphene.InputObjectType):
    email = graphene.String(
        required=True,
        description=("Email of the user that will be used for password recovery."),
    )


class ChangePasswordInput(graphene.InputObjectType):
    old_password = graphene.String(required=False, description="Old password")
    new_password1 = graphene.String(required=True, description="New password")
    new_password2 = graphene.String(required=True, description="Repeat new password")


class ChangePassword(ModelMutation):
    AUTHENTICATION_ERROR = "You must be logged in"
    MISSING_INPUT = "Missing input information"
    INVALID_OLD_PASSWORD = "Invalid old password"
    INVALID_NEW_PASSWORDS = "New password does not match"
    INVALID_OLD_AND_NEW_PASS = "New and old passwords may not be equal"

    class Arguments:
        input = ChangePasswordInput(required=True, description="Change password input")

    class Meta:
        description = "Change password for signed in users"
        model = models.User

    @classmethod
    def get_instance(cls, info, **data):
        if info.context.user.is_authenticated:
            return info.context.user
        raise ValidationError({"authentication": cls.AUTHENTICATION_ERROR})

    @classmethod
    def clean_input(cls, info, user, data):
        clean_input = super().clean_input(info, user, data)
        old_password = clean_input.get("old_password")
        new_password1 = clean_input.get("new_password1")
        new_password2 = clean_input.get("new_password2")
        if not new_password1 or not new_password2:
            raise ValidationError({"missing_input": cls.MISSING_INPUT})
        if old_password:
            if not user.check_password(old_password):
                raise ValidationError({"old_password": cls.INVALID_OLD_PASSWORD})
        elif not new_password1 == new_password2:
            raise ValidationError({"new_password": cls.INVALID_NEW_PASSWORDS})
        elif old_password == new_password1:
            raise ValidationError({"new_password": cls.INVALID_OLD_AND_NEW_PASS})
        else:
            return clean_input

    @classmethod
    def save(cls, info, user, cleaned_input):
        user.set_password(cleaned_input["new_password1"])
        user.save()


class CustomerPasswordReset(BaseMutation):
    class Arguments:
        input = CustomerPasswordResetInput(
            description="Fields required to reset customer's password", required=True
        )

    class Meta:
        description = "Resets the customer's password."

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        email = data.get("input")["email"]
        try:
            user = models.User.objects.get(email=email)
        except ObjectDoesNotExist:
            raise ValidationError({"email": "User with this email doesn't exist"})
        site = info.context.site
        send_user_password_reset_email(user, site)
        return CustomerPasswordReset()


class SetNewPasswordInput(graphene.InputObjectType):
    token = graphene.String(required=True)
    # email = graphene.String(required=True)
    uidb64 = graphene.String(required=True)
    new_password = graphene.String(required=True)


class SetNewPassword(BaseMutation):
    INVALID_TOKEN = "Invalid or expired token."

    class Arguments:
        input = SetNewPasswordInput(required=True)

    class Meta:
        description = "Set new password"

    @classmethod
    def clean_input(cls, instance, data):
        token = data.pop("token")
        if not default_token_generator.check_token(instance, token):
            raise ValidationError({"token": SetNewPassword.INVALID_TOKEN})
        return data

    @classmethod
    def get_user(cls, uidb64):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = models.User.objects.get(pk=uid)
        except (
            TypeError,
            ValueError,
            OverflowError,
            ObjectDoesNotExist,
            ValidationError,
        ):
            user = None
        return user

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        uidb64 = data.get("input")["uidb64"]
        user = cls.get_user(uidb64)
        if user:
            clean_input = cls.clean_input(user, data.get("input"))
            user.set_password(clean_input["new_password"])
            user.save()
            return SetNewPassword()
        raise ValidationError({"email": "User with this email doesn't exist"})


class AddressCreate(ModelMutation):
    user = graphene.Field(
        User, description="A user instance for which the address was created."
    )

    class Arguments:
        input = AddressInput(
            description="Fields required to create address", required=True
        )

    class Meta:
        description = "Creates user address"
        model = models.Address

    @classmethod
    def clean_phone_number(cls, input_data={}):
        # phone = input_data.get("phone")
        return True

    @classmethod
    def clean_zip_code(cls, input_data):
        # zip_code = input_data.get("postal_code")
        return True

    @classmethod
    def perform_mutation(cls, root, info, **data):
        user = get_user_instance(info)
        input_data = data.get("input")
        if cls.clean_phone_number(input_data) and cls.clean_zip_code(input_data):
            response = super().perform_mutation(root, info, **data)
            if not response.errors:
                user.addresses.add(response.address)
                response.user = user
            return response
        return cls(user=None)


class AddressUpdate(ModelMutation):
    user = graphene.Field(
        User, description="A user instance for which the address was edited."
    )

    class Arguments:
        id = graphene.ID(description="ID of the address to update", required=True)
        input = AddressInput(
            description="Fields required to update address", required=True
        )

    class Meta:
        description = "Updates an address"
        model = models.Address
        exclude = ["user_addresses"]

    @classmethod
    def clean_input(cls, info, instance, data):
        # Method check_permissions cannot be used for permission check, because
        # it doesn't have the address instance.
        if not can_edit_address(
            info.context.user, instance, check_user_permission=False
        ):
            raise PermissionDenied()
        return super().clean_input(info, instance, data)

    @classmethod
    def perform_mutation(cls, root, info, **data):
        response = super().perform_mutation(root, info, **data)
        user = response.address.user_addresses.first()
        response.user = user
        return response


class AddressDelete(ModelDeleteMutation):
    user = graphene.Field(
        User, description="A user instance for which the address was deleted."
    )

    class Arguments:
        id = graphene.ID(required=True, description="ID of the address to delete.")

    class Meta:
        description = "Deletes an address"
        model = models.Address

    @classmethod
    def clean_instance(cls, info, instance):
        # Method check_permissions cannot be used for permission check, because
        # it doesn't have the address instance.
        if not can_edit_address(
            info.context.user, instance, check_user_permission=False
        ):
            raise PermissionDenied()
        return super().clean_instance(info, instance)

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        if not cls.check_permissions(info.context.user):
            raise PermissionDenied()

        node_id = data.get("id")
        instance = cls.get_node_or_error(info, node_id, Address)
        if instance:
            cls.clean_instance(info, instance)

        db_id = instance.id

        # Return the first user that the address is assigned to. There is M2M
        # relation between users and addresses, but in most cases address is
        # related to only one user.
        user = instance.user_addresses.first()

        instance.delete(user=user)

        instance.id = db_id

        response = cls.success_response(instance)

        # Refresh the user instance to clear the default addresses. If the
        # deleted address was used as default, it would stay cached in the
        # user instance and the invalid ID returned in the response might cause
        # an error.
        user.refresh_from_db()

        response.user = user
        return response


class RecipientCreate(ModelMutation):
    recipient = graphene.Field(
        Recipient, description="A recipient instance created."
    )

    class Arguments:
        input = RecipientInput(
            description="Fields required to create recipient", required=True
        )

    class Meta:
        description = "Create a recipient."
        model = models.Recipient

    @classmethod
    def perform_mutation(cls, root, info, **data):
        user = get_user_instance(info)
        input_data = data.get("input")
        response = super().perform_mutation(root, info, **data)
        if not response.errors:
            response.recipient.user_id = user.id
            response.recipient.user_email = user.email
            user.recipients = response.recipient
            user.save()
            return response
        return cls(recipient=None)
      

class SendPhoneVerificationSMS(BaseMutation):
    status = graphene.Field(ValidatePhoneStatusEnum)

    class Arguments:
        user_id = graphene.ID(
            description="User ID to submit the verification code.", required=True
        )

    class Meta:
        description = "Send a code to validate the phone number"

    @classmethod
    def perform_mutation(cls, _root, info, user_id):
        try:
            user = models.User.objects.get(id=user_id)
        except ObjectDoesNotExist:
            raise ValidationError({"userID": "User with this ID doesn't exist"})
        if user.is_phone_verified:
            raise ValidationError({"isPhoneVerified": "Phone number of the user already verified"})
        else:
            try:
                response = send_code(str(user.phone))
            except TwilioRestException as e:
                raise ValidationError({"twilio_service": e.msg})
        if response.status == "pending" and response.valid is False:
            status = ValidatePhoneStatusEnum.PROCEED
        return cls(status=status)


class VerifySMSCodeVerification(BaseMutation):
    status = graphene.Field(ValidatePhoneStatusEnum)

    class Arguments:
        user_id = graphene.ID(
            description="User ID to submit the verification code.", required=True
        )
        code = graphene.String(
            description="Verification code.", required=True
        )

    class Meta:
        description = "check the code to validate the phone number"

    @classmethod
    def perform_mutation(cls, _root, info, user_id, code):
        try:
            user = models.User.objects.get(id=user_id)
        except ObjectDoesNotExist:
            raise ValidationError({"userID": "User with this ID doesn't exist"})
        if user.is_phone_verified:
            raise ValidationError({"isPhoneVerified": "Phone number of the user already verified"})
        else:
            try:
                response = check_code(str(user.phone), code)
            except TwilioRestException as e:
                raise ValidationError({"twilio_service": e.msg})
        if response.status == "approved" and response.valid is True:
            status = ValidatePhoneStatusEnum.APPROVED
            user.is_phone_verified = True
            user.save()
        elif response.status == "pending" and response.valid is False:
            status = ValidatePhoneStatusEnum.REJECTED
        return cls(status=status)
