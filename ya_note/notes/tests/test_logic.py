from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TEXT = 'Текст'
    TITLE_TEXT = 'Заголовок'
    NEW_COMMENT_TEXT = 'Новый текст'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.notes = Note.objects.create(
            title=cls.NOTE_TEXT,
            text=cls.TITLE_TEXT,
            author=cls.user
        )

        cls.url = reverse('notes:detail', args=(cls.notes.slug,))

        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'title': cls.TITLE_TEXT,
            'text': cls.TITLE_TEXT,
            'slug': 'new-slug'
        }

    def test_anonymous_user_cant_create_note(self):
        notes_count_before = Note.objects.count()
        self.client.post(self.url, data=self.form_data)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)

    def test_cant_create_identical_slug(self):
        url = reverse('notes:add')
        self.form_data['slug'] = self.notes.slug
        response = self.auth_client.post(url, data=self.form_data)
        self.assertFormError(
            response,
            'form',
            'slug',
            self.notes.slug + WARNING
        )

    def test_empty_slug_auto_generated(self):
        expected_slug = slugify(self.notes.title)
        response = self.auth_client.get(
            reverse('notes:detail', args=(expected_slug,))
        )
        self.assertEqual(response.status_code, 200)

    def test_note_edit_and_delete(self):
        url = reverse('notes:edit', args=(self.notes.slug,))
        response = self.auth_client.post(url, self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.notes.refresh_from_db()
        self.assertEqual(self.notes.title, self.form_data['title'])
        self.assertEqual(self.notes.text, self.form_data['text'])
        self.assertEqual(self.notes.slug, self.form_data['slug'])


class TestNoteEditDelete(TestCase):
    NOTE_TEXT = 'Текст'
    TITLE_TEXT = 'Заголовок'
    NEW_NOTE_TEXT = 'Новый текст'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор комментария')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.notes = Note.objects.create(
            title=cls.TITLE_TEXT,
            text=cls.NOTE_TEXT,
            author=cls.author
        )
        cls.succes = reverse('notes:success')
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.edit_url = reverse('notes:edit', args=(cls.notes.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.notes.slug,))
        cls.form_data = {
            'title': cls.TITLE_TEXT,
            'text': cls.NEW_NOTE_TEXT,
            'slug': 'new-slug'
        }

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.succes)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        comments_count = Note.objects.count()
        self.assertEqual(comments_count, 1)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.succes)
        self.notes.refresh_from_db()
        self.assertEqual(self.notes.text, self.NEW_NOTE_TEXT)

    def test_user_cant_edit_comment_of_another_user(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.notes.refresh_from_db()
        self.assertEqual(self.notes.text, self.NOTE_TEXT)
