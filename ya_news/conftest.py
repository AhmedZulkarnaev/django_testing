import pytest
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username="Автор")


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news_count():
    today = datetime.today()
    all_news = [
        News(
            title=f"Новость {index}",
            text="Просто текст.",
            date=today - timedelta(days=index),
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    news = News.objects.bulk_create(all_news)
    return news


@pytest.fixture
def news(author):
    new = News.objects.create(
        title="Заголовок",
        text="Текст заметки",
    )
    return new


@pytest.fixture
def comment_count(author, news):
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f"Tекст {index}",
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    return comment


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        text="Текст заметки",
        author=author,
        news=news,
    )
    return comment


@pytest.fixture
def id_for_args(news):
    return (news.id,)


@pytest.fixture
def id_for_comment(comment):
    return (comment.pk,)


@pytest.fixture
def form_data():
    return {
        "text": "Новый текст",
    }
