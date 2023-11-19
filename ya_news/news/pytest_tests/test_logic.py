from http import HTTPStatus
from django.urls import reverse
import pytest
from pytest_django.asserts import assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_authenticated_user_can_create_comment(
    author_client, news, form_data, id_for_args
):
    url = reverse("news:detail", args=(id_for_args))
    author_client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 1


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data):
    url = ("news:detail", pytest.lazy_fixture("id_for_args"))
    client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_use_bad_words(author_client, news, id_for_args):
    bad_words_data = {"text": f"Какой-то текст, {BAD_WORDS[0]}, еще текст"}
    url = reverse("news:detail", args=(id_for_args))
    response = author_client.post(url, data=bad_words_data)
    assert response.status_code == HTTPStatus.OK

    assertFormError(response, form="form", field="text", errors=WARNING)

    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_edit_comment(
        author_client, form_data, comment, id_for_comment
):
    url = reverse("news:edit", args=id_for_comment)
    response = author_client.post(url, form_data)
    assert response.status_code == HTTPStatus.FOUND
    comment.refresh_from_db()
    assert comment.text == form_data["text"]


def test_other_user_cant_edit_comment(
        admin_client, form_data, news, comment, id_for_args
):
    url = reverse("news:edit", args=(id_for_args))
    response = admin_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text


def test_author_can_delete_note(author_client, id_for_args, comment):
    url = reverse("news:delete", args=id_for_args)
    response = author_client.post(url)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


def test_other_user_cant_delete_note(admin_client, id_for_args, comment):
    url = reverse("news:delete", args=id_for_args)
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
