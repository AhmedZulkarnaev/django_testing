import pytest
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from django.urls import reverse

from news.models import News, Comment


@pytest.fixture
def anonymous_client(client):
    return client


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username="Автор")


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
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
def new(author):
    new = News.objects.create(
        title="Заголовок",
        text="Текст новости",
    )
    return new


@pytest.fixture
def comments(author, new):
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=new,
            author=author,
            text=f"Tекст {index}",
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    return comment


@pytest.fixture
def comment(author, new):
    comment = Comment.objects.create(
        text="Текст заметки",
        author=author,
        news=new,
    )
    return comment


@pytest.fixture
def news_id(new):
    return new.id,


@pytest.fixture
def comment_id(comment):
    return comment.id,


@pytest.fixture
def form_data():
    return {
        "text": "Новый текст",
        "new": new,
    }


@pytest.fixture
def news_delete_url(comment_id):
    return reverse("news:delete", args=comment_id)


@pytest.fixture
def news_detail_url(news_id):
    return reverse("news:detail", args=news_id)


@pytest.fixture
def news_edit_url(comment_id):
    return reverse("news:edit", args=comment_id)
