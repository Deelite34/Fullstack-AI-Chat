from fastapi import HTTPException
import pytest

from services.exceptions import CredentialsAlreadyUsed


def test_create_new_user(user_repository, random_user_schema):
    user = user_repository.create_user(random_user_schema)

    assert user is not None
    assert user.username == random_user_schema.username
    assert user.email == random_user_schema.email
    assert user.id is not None


def test_create_new_user_raises_duplicate_username_or_email(
    user_repository, user_schema_factory
):
    user_schema_1 = user_schema_factory(1)
    user_repository.create_user(user_schema_1)

    with pytest.raises(CredentialsAlreadyUsed) as excinfo:
        user_repository.create_user(user_schema_1)

    assert "This username or email is not available." in str(excinfo.value)


def test_list_users_returns_all_created_users(user_repository, user_schema_factory):
    first_user_schema = user_schema_factory(3)
    second_user_schema = user_schema_factory(
        4, username="testuser-list-2", email="list_test_2@example.com"
    )

    first_user = user_repository.create_user(first_user_schema)
    second_user = user_repository.create_user(second_user_schema)

    users = user_repository.list_users()

    assert len(users) == 2
    assert first_user in users
    assert second_user in users


def test_get_by_email_returns_matching_user(user_repository, user_schema_factory):
    user_schema = user_schema_factory(
        5, username="user_lookup_email", email="lookup_email@example.com"
    )
    created_user = user_repository.create_user(user_schema)

    fetched_user = user_repository.get_by_email(user_schema.email)

    assert fetched_user is not None
    assert fetched_user.id == created_user.id
    assert fetched_user.username == created_user.username
    assert fetched_user.email == created_user.email


def test_get_by_id_returns_matching_user(user_repository, user_schema_factory):
    user_schema = user_schema_factory(
        6, username="user_lookup_id", email="lookup_id@example.com"
    )
    created_user = user_repository.create_user(user_schema)

    fetched_user = user_repository.get_by_id(created_user.id)

    assert fetched_user is not None
    assert fetched_user.id == created_user.id
    assert fetched_user.username == created_user.username


def test_get_by_username_returns_matching_user(user_repository, user_schema_factory):
    user_schema = user_schema_factory(
        7, username="user_lookup_username", email="lookup_username@example.com"
    )
    created_user = user_repository.create_user(user_schema)

    fetched_user = user_repository.get_by_username(user_schema.username)

    assert fetched_user is not None
    assert fetched_user.id == created_user.id
    assert fetched_user.email == created_user.email


def test_lookup_methods_return_none_for_missing_values(user_repository):
    assert user_repository.get_by_email("missing@example.com") is None
    assert user_repository.get_by_id(999999) is None
    assert user_repository.get_by_username("missing_user") is None


def test_check_user_by_username_exists_reports_presence_and_absence(
    user_repository, user_schema_factory
):
    user_schema = user_schema_factory(
        8, username="user_check_exists", email="check_exists@example.com"
    )
    created_user = user_repository.create_user(user_schema)

    assert user_repository.check_user_by_username_exists(user_schema.username) is not None
    assert user_repository.check_user_by_username_exists(user_schema.username).id == created_user.id
    assert user_repository.check_user_by_username_exists("not_a_real_user") is None
