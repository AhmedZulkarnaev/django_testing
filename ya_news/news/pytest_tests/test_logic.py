from http import HTTPStatus

from django.urls import reverse
import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_authenticated_user_can_post_comment(
    author_client, new, form_data, news_id, comment, author
):
    """Авторизованный юзер может комментировать"""
    url = reverse("news:detail", args=news_id)
    Comment.objects.all().delete()
    comment_before = Comment.objects.count()
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    comments_after = Comment.objects.count()
    assert comments_after == comment_before + 1
    get_comment = Comment.objects.get(news=new)
    assert get_comment.author == author
    assert get_comment.text == form_data['text']


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data):
    """Анонимный юзер не может комментировать"""
    comments_before = Comment.objects.count()
    url = ("news:detail", pytest.lazy_fixture("news_id"))
    client.post(url, data=form_data)
    comments_after = Comment.objects.count()
    assert comments_after == comments_before


def test_user_cant_use_bad_words(author_client, new, news_id):
    """Юзер не может писать запрещенные слова"""
    comments_before = Comment.objects.count()
    bad_words_data = {"text": {BAD_WORDS[0]}}
    url = reverse("news:detail", args=(news_id))
    response = author_client.post(url, data=bad_words_data)
    assert response.status_code == HTTPStatus.OK
    assertFormError(response, form="form", field="text", errors=WARNING)
    comments_after = Comment.objects.count()
    assert comments_after == comments_before


def test_author_can_edit_comment(
        author_client, form_data, comment, comment_id, new, author
):
    """Автор может редактировать комментарии"""
    url = reverse("news:edit", args=comment_id)
    response = author_client.post(url, form_data)
    assert response.status_code == HTTPStatus.FOUND
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.news == new


def test_other_user_cant_edit_comment(
        admin_client, form_data, comment, new, comment_id, author
):
    """Другой юзер не может редактировать комментарии"""
    url = reverse("news:edit", args=(comment_id))
    response = admin_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from.text
    assert comment.author == author
    assert comment.news == new


def test_author_can_delete_comment(author_client, comment_id, comment):
    """Автор может удалять комментарии"""
    url = reverse("news:delete", args=comment_id)
    response = author_client.post(url)
    assert response.status_code == HTTPStatus.FOUND
    assert not Comment.objects.filter(id=comment.id).exists()


def test_other_user_cant_delete_comment(admin_client, comment_id, comment):
    """Другой юзер не может удалять комментарии"""
    url = reverse("news:delete", args=comment_id)
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.filter(id=comment.id).exists()
