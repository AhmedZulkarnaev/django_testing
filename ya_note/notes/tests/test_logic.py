from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from http import HTTPStatus

from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING


User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TEXT = 'Текст'
    TITLE_TEXT = 'Заголовок'

    NEW_TITLE = 'Новый заголовок'
    NEW_NOTE_TEXT = 'Новый текст'
    SLUG = 'slug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Мимо Крокодил')
        cls.notes = Note.objects.create(
            title=cls.TITLE_TEXT,
            text=cls.NOTE_TEXT,
            author=cls.author
        )
        cls.reader = User.objects.create(username='Пользователь')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.other_client = Client()
        cls.other_client.force_login(cls.reader)

        cls.form_data = {
            'author': cls.author,
            'title': cls.NEW_TITLE,
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.SLUG,
        }
        cls.login_url = reverse('users:login')
        cls.detail_url = reverse('notes:detail', args=(cls.notes.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.notes.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.notes.slug,))
        cls.add_url = reverse('notes:add')
        cls.success = reverse('notes:success')

    def test_auth_user_can_create_note(self):
        """Авторизованный юзер может создать заметку"""
        notes_count_before = Note.objects.count()
        self.auth_client.post(self.add_url, data=self.form_data)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before + 1)
        new_note = Note.objects.get(pk=self.notes.pk)
        self.assertEqual(self.notes.author, new_note.author)
        self.assertEqual(self.notes.title, new_note.title)
        self.assertEqual(self.notes.text, new_note.text)

    def test_anonymous_user_cant_create_note(self):
        """Анонимный юзер не может создать заметку"""
        notes_count_before = Note.objects.count()
        self.client.post(self.add_url, data=self.form_data)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)

    def test_cant_create_identical_slug(self):
        """Юзер не может создать одинаковые slug"""
        url = reverse('notes:add')
        self.form_data['slug'] = self.notes.slug
        initial_note_count = Note.objects.count()
        response = self.auth_client.post(url, data=self.form_data)
        self.assertFormError(
            response,
            'form',
            'slug',
            self.notes.slug + WARNING
        )
        final_note_count = Note.objects.count()
        self.assertEqual(initial_note_count, final_note_count)

    def test_author_can_note_edit(self):
        """Автор может редактировать заметку"""
        url = reverse('notes:edit', args=(self.notes.slug,))
        response = self.auth_client.post(url, self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.notes.refresh_from_db()
        self.assertEqual(self.notes.author, self.author)
        self.assertEqual(self.notes.title, self.form_data['title'])
        self.assertEqual(self.notes.text, self.form_data['text'])

    def test_author_can_delete_note(self):
        """Автор может удалить заметку"""
        response = self.auth_client.delete(self.delete_url)
        self.assertRedirects(response, self.success)
        self.assertFalse(Note.objects.filter(pk=self.notes.pk).exists())

    def test_other_author_cant_note_edit(self):
        """Пользователь не может редактировать чужую заметку"""
        response = self.other_client.post(self.edit_url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.notes.refresh_from_db()
        note = Note.objects.get(pk=self.notes.pk)
        self.assertEqual(self.notes.author, note.author)
        self.assertEqual(self.notes.title, note.title)
        self.assertEqual(self.notes.text, note.text)

    def test_user_cant_delete_note_of_another_user(self):
        """Пользователь не может удалить чужую заметку"""
        response = self.other_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(Note.objects.filter(pk=self.notes.pk).exists())

    def test_generate_slug_if_field_empty(self):
        """Поле slug автогенерируется, если поле пустое"""
        self.form_data.pop('slug')
        response = self.auth_client.post(self.add_url, data=self.form_data)
        self.assertEqual(response.status_code, 302)
        new_note = Note.objects.latest('id')
        self.assertTrue(new_note.slug)
        self.assertEqual(new_note.slug, slugify(new_note.title))
