from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from notes.models import Note


User = get_user_model()


class TestFormPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Просто текст.',
            author=cls.author,
        )
        cls.author_two = User.objects.create(username='Александр Пушкин')
        cls.another_note = Note.objects.create(
            title='Еще одна заметка',
            text='Еще текст.',
            author=cls.author_two,
        )

    def test_notes_of_one_user_only(self):
        url = reverse('notes:list')
        self.client.force_login(self.author)
        response = self.client.get(url)
        self.assertIn('object_list', response.context)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)
        self.assertNotIn(self.another_note, object_list)

    def test_user_has_form(self):
        url = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        )
        for url, args in url:
            with self.subTest(url=url):
                url = reverse(url, args=args)
                self.client.force_login(self.author)
                response = self.client.get(url)
                self.assertIn('form', response.context)
