import json

from ..utils import assert_no_permission, get_graphql_content

from mesada.account.models import User


def test_token_create(api_client, user):
    query = """
    mutation tokenCreate($email: String!, $password: String!) {
        tokenCreate(email: $email, password: $password) {
            token
            payload
            refreshExpiresIn
        }
    }
    """
    variables_values = {"email": user.email, "password": "password"}
    response = api_client.post_graphql(query, variables_values)
    content = get_graphql_content(response)
    data = content["data"]["tokenCreate"]

    assert data["token"]


def test_token_create_bad_password(api_client, user):
    query = """
    mutation tokenCreate($email: String!, $password: String!) {
        tokenCreate(email: $email, password: $password) {
            token
            payload
            refreshExpiresIn
        }
    }
    """
    variables_values = {"email": user.email, "password": "MAL"}
    response = api_client.post_graphql(query, variables_values)

    content = json.loads(response.content)

    # TODO: translate
    assert content["errors"][0]["message"] == "Please enter valid credentials"


def test_token_create_bad_email(api_client, user):
    query = """
    mutation tokenCreate($email: String!, $password: String!) {
        tokenCreate(email: $email, password: $password) {
            token
            payload
            refreshExpiresIn
        }
    }
    """
    variables_values = {"email": "bad@bad.com", "password": "password"}
    response = api_client.post_graphql(query, variables_values)

    content = json.loads(response.content)

    # TODO: translate
    assert content["errors"][0]["message"] == "Please enter valid credentials"


def test_customer_register(api_client):
    query = """
    mutation customerRegister($input: CustomerRegisterInput!) {
        customerRegister(input: $input) {
            token
            user {
                id
                firstName
                lastName
                isStaff
                isActive
                email
            }
            errors {
                field
                message
            }
        }
    }
    """
    variables_values = {
        "input": {
            "email": "test@mail.com",
            "firstName": "Kayser",
            "lastName": "Zose",
            "phone": "+525548919112",
            "password": "12345",
        }
    }
    response = api_client.post_graphql(query, variables_values)
    content = get_graphql_content(response)
    data = content["data"]["customerRegister"]

    assert data["token"]
    assert data["user"]
    assert data["user"]["email"] == "test@mail.com"

    assert User.objects.filter(email="test@mail.com").exists()


def test_customer_register_bad_email(api_client):
    query = """
    mutation customerRegister($input: CustomerRegisterInput!) {
        customerRegister(input: $input) {
            token
            user {
                id
                firstName
                lastName
                isStaff
                isActive
                email
            }
            errors {
                field
                message
            }
        }
    }
    """
    variables_values = {
        "input": {
            "email": "testmail.com",
            "firstName": "Kayser",
            "lastName": "Zose",
            "phone": "+525548919112",
            "password": "12345",
        }
    }
    response = api_client.post_graphql(query, variables_values)
    content = get_graphql_content(response)
    data = content["data"]["customerRegister"]

    assert data["token"] is None
    # TODO: Translate!
    assert data["errors"][0]["message"] == "Enter a valid email address."


def test_customer_register_bad_phone(api_client):
    query = """
    mutation customerRegister($input: CustomerRegisterInput!) {
        customerRegister(input: $input) {
            token
            user {
                id
                firstName
                lastName
                isStaff
                isActive
                email
            }
            errors {
                field
                message
            }
        }
    }
    """
    variables_values = {
        "input": {
            "email": "test@mail.com",
            "firstName": "Kayser",
            "lastName": "Zose",
            "phone": "5548919112",
            "password": "12345",
        }
    }
    response = api_client.post_graphql(query, variables_values)
    content = get_graphql_content(response)
    data = content["data"]["customerRegister"]

    assert data["token"] is None
    assert data["errors"][0]["field"] == "phone"
    # TODO: Translate!
    assert data["errors"][0]["message"] == "The phone number entered is not valid."


def test_query_customers(staff_api_client, user_api_client, permission_manage_users):
    query = """
    query Users {
        customers(first: 20) {
            totalCount
            edges {
                node {
                    isStaff
                    email
                }
            }
        }
    }
    """
    variables_values = {}

    response = staff_api_client.post_graphql(
        query, variables_values, permissions=[permission_manage_users]
    )
    content = get_graphql_content(response)
    users = content["data"]["customers"]["edges"]
    assert users
    assert all([not user["node"]["isStaff"] for user in users])

    # check permissions
    response = user_api_client.post_graphql(query, variables_values)
    assert_no_permission(response)
