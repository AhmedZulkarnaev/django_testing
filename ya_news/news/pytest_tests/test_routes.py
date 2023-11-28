from http import HTTPStatus

from django.urls import reverse
import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    "name, user, user_status",
    (
        (
            reverse("news:home"),
            pytest.lazy_fixture("anonymous_client"),
            HTTPStatus.OK
        ),
        (
            reverse("users:login"),
            pytest.lazy_fixture("anonymous_client"),
            HTTPStatus.OK
        ),
        (
            reverse("users:logout"),
            pytest.lazy_fixture("anonymous_client"),
            HTTPStatus.OK
        ),
        (
            reverse("users:signup"),
            pytest.lazy_fixture("anonymous_client"),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture("news_detail_url"),
            pytest.lazy_fixture("anonymous_client"),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture("news_edit_url"),
            pytest.lazy_fixture("author_client"),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture("news_delete_url"),
            pytest.lazy_fixture("author_client"),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture("news_edit_url"),
            pytest.lazy_fixture("admin_client"),
            HTTPStatus.NOT_FOUND
        ),
        (
            pytest.lazy_fixture("news_delete_url"),
            pytest.lazy_fixture("admin_client"),
            HTTPStatus.NOT_FOUND
        ),

    ),
)
def test_pages_availability_for_differents_user(
    client, name, user, user_status
):
    response = user.get(name)
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
