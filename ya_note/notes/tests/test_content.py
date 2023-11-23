from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

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
        cls.other_author = User.objects.create(username='Александр Пушкин')
        cls.another_note = Note.objects.create(
            title='Еще одна заметка',
            text='Еще текст.',
            author=cls.other_author,
        )

    def test_notes_of_one_user_only(self):
        """Заметки одного юзера не попадают в заметки другого"""
        data = (
            (self.note, True),
            (self.another_note, False),
        )
        for note, value in data:
            with self.subTest(note=note, value=value):
                url = reverse('notes:list')
                self.client.force_login(self.author)
                response = self.client.get(url)
                object_list = response.context['object_list']
                self.assertEqual(value, note in object_list)

    def test_user_has_form(self):
        """У пользователся отображается форма"""
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
                form = response.context['form']
                self.assertIsInstance(form, NoteForm)
