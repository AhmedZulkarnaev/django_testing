from http import HTTPStatus

from pytest_django.asserts import assertRedirects
from django.urls import reverse

import pytest


@pytest.mark.django_db
@pytest.mark.parametrize(
    "name, args, user, user_status",
    (
        ("news:home", None, None, HTTPStatus.OK),
        ("users:login", None, None, HTTPStatus.OK),
        ("users:logout", None, None, HTTPStatus.OK),
        ("users:signup", None, None, HTTPStatus.OK),
        ("news:detail", pytest.lazy_fixture("news_id"), None, HTTPStatus.OK),
        (
            "news:edit",
            pytest.lazy_fixture("comment_id"),
            pytest.lazy_fixture("author_client"),
            HTTPStatus.OK
        ),
        (
            "news:delete",
            pytest.lazy_fixture("comment_id"),
            pytest.lazy_fixture("author_client"),
            HTTPStatus.OK
        ),
        (
            "news:edit",
            pytest.lazy_fixture("comment_id"),
            pytest.lazy_fixture("admin_client"),
            HTTPStatus.NOT_FOUND
        ),
        (
            "news:delete",
            pytest.lazy_fixture("comment_id"),
            pytest.lazy_fixture("admin_client"),
            HTTPStatus.NOT_FOUND
        ),

    ),
)
def test_pages_availability_for_differents_user(
    client, name, args, user, user_status
):
    url = reverse(name, args=args)
    if user:
        response = user.get(url)
    else:
        response = client.get(url)
    assert response.status_code == user_status


@pytest.mark.parametrize(
    "name, args",
    (
        ("news:edit", pytest.lazy_fixture("comment_id")),
        ("news:delete", pytest.lazy_fixture("comment_id")),
    ),
)
def test_redirects(client, name, args):
    login_url = reverse("users:login")
    url = reverse(name, args=args)
    expected_url = f"{login_url}?next={url}"
    response = client.get(url)
    assertRedirects(response, expected_url)
