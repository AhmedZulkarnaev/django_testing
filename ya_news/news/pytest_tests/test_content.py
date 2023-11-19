from django.urls import reverse
from django.conf import settings
import pytest

from news.models import Comment

HOME_URL = reverse("news:home")


@pytest.mark.django_db
def test_count_news(client, news_count):
    response = client.get(HOME_URL)
    object_list = response.context["object_list"]
    assert len(object_list) == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, news_count):
    response = client.get(HOME_URL)
    object_list = response.context["object_list"]
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, comment_count):
    response = client.get(HOME_URL)
    object_list = response.context["object_list"]
    comments = [obj for obj in object_list if isinstance(obj, Comment)]
    comment_dates = [comment.created for comment in comments]
    assert comment_dates == sorted(comment_dates, reverse=False)


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(
    "parametrized_client, news_in_list",
    (
        (pytest.lazy_fixture("author_client"), True),
        (pytest.lazy_fixture("client"), False),
    ),
)
def test_different_users_has_form(parametrized_client, news, news_in_list):
    detail_url = reverse("news:detail", args=(news.id,))
    response = parametrized_client.get(detail_url)
    assert ("form" in response.context) is news_in_list