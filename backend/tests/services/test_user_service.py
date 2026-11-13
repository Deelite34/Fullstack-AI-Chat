def test_create_user_returns_user_schema(user_service, random_user_schema):
    created_user = user_service.create_user(random_user_schema)

    assert created_user.id is not None
    assert created_user.username == random_user_schema.username
    assert created_user.email == random_user_schema.email


def test_list_users_returns_all_users(user_service, user_schema_factory):
    first_user = user_service.create_user(user_schema_factory(1))
    second_user = user_service.create_user(
        user_schema_factory(
            2, username="service-list-2", email="service_list_2@example.com"
        )
    )

    users = user_service.list_users()

    assert len(users.users) == 2
    assert any(user.username == first_user.username for user in users.users)
    assert any(user.email == second_user.email for user in users.users)
    assert all(user.id is not None for user in users.users)
