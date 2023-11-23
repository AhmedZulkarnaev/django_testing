from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.notes = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
        )

    def test_auth_user_permissions(self):
        """Доступ к страницам разным пользователям"""
        urls = (
            ('notes:home', None, None, HTTPStatus.OK),
            ('users:login', None, None, HTTPStatus.OK),
            ('users:logout', None, None, HTTPStatus.OK),
            ('users:signup', None, None, HTTPStatus.OK),
            ('notes:edit', (self.notes.slug,), self.author, HTTPStatus.OK),
            ('notes:detail', (self.notes.slug,), self.author, HTTPStatus.OK),
            ('notes:delete', (self.notes.slug,), self.author, HTTPStatus.OK),
            (
                'notes:edit',
                (self.notes.slug,),
                self.reader,
                HTTPStatus.NOT_FOUND
            ),
            (
                'notes:detail',
                (self.notes.slug,),
                self.reader,
                HTTPStatus.NOT_FOUND
            ),
            (
                'notes:delete',
                (self.notes.slug,),
                self.reader,
                HTTPStatus.NOT_FOUND
            ),
            ('notes:list', None, self.reader, HTTPStatus.OK),
            ('notes:success', None, self.reader, HTTPStatus.OK),
            ('notes:add', None, self.reader, HTTPStatus.OK),
        )
        for url_name, arg, user, status in urls:
            with self.subTest(url_name=url_name, user=user):
                url = reverse(url_name, args=arg)
                if user:
                    self.client.force_login(user)
                    response = self.client.get(url)
                else:
                    response = self.client.get(url)
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
