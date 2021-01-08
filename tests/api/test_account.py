from ..utils import get_graphql_content, assert_no_permission


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
