from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.reader = User.objects.create(username='reader')
        cls.notes = Note.objects.create(
            title='Title',
            text='Text',
            author=cls.author
        )
        cls.anonymous_client = Client()
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

    def test_auth_user_permissions(self):
        """Доступ к страницам разным пользователям"""
        urls = (
            ('notes:home', None, self.anonymous_client, HTTPStatus.OK),
            ('users:login', None, self.anonymous_client, HTTPStatus.OK),
            ('users:logout', None, self.anonymous_client, HTTPStatus.OK),
            ('users:signup', None, self.anonymous_client, HTTPStatus.OK),
            (
                'notes:edit',
                (self.notes.slug,),
                self.author_client,
                HTTPStatus.OK
            ),
            (
                'notes:detail',
                (self.notes.slug,),
                self.author_client,
                HTTPStatus.OK
            ),
            (
                'notes:delete',
                (self.notes.slug,),
                self.author_client,
                HTTPStatus.OK
            ),
            (
                'notes:edit',
                (self.notes.slug,),
                self.reader_client,
                HTTPStatus.NOT_FOUND
            ),
            (
                'notes:detail',
                (self.notes.slug,),
                self.reader_client,
                HTTPStatus.NOT_FOUND
            ),
            (
                'notes:delete',
                (self.notes.slug,),
                self.reader_client,
                HTTPStatus.NOT_FOUND
            ),
            ('notes:list', None, self.reader_client, HTTPStatus.OK),
            ('notes:success', None, self.reader_client, HTTPStatus.OK),
            ('notes:add', None, self.reader_client, HTTPStatus.OK),
        )
        for url_name, arg, client, status in urls:
            with self.subTest(url_name=url_name):
                url = reverse(url_name, args=arg)
                response = client.get(url)
                self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Проверка редиректа на страницу логина"""
        login_url = reverse('users:login')

        urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:edit', (self.notes.slug,)),
            ('notes:detail', (self.notes.slug,)),
            ('notes:delete', (self.notes.slug,)),
        )

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
