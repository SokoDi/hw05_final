import shutil
import tempfile

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from ..models import Post, Group, Comment, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='author')
        cls.group = Group.objects.create(
            title='Тестовое название',
            slug='test-slug',
            description='Тестовое описание',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.group1 = Group.objects.create(
            title='Другое название',
            slug='test2-slug',
            description='Другое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_create(self):
        """Создание поста прошло успешно."""
        posts_count = Post.objects.count()

        form_data = {
            'group': self.group.id,
            'text': 'Тестовый пост',
            'image': self.uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        post_latest = Post.objects.latest('id')
        self.assertRedirects(
            response, reverse('posts:profile', args=[
                self.user.username]))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(post_latest.text, form_data['text'])
        self.assertEqual(post_latest.group.id, form_data['group'])
        self.assertEqual(post_latest.image, 'posts/small.gif')

    def test_post_edit(self):
        """Редактирование поста прошло успешно."""
        post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group,
            image=self.uploaded
        )

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded1 = SimpleUploadedFile(
            name='small_new.gif',
            content=small_gif,
            content_type='image/gif'
        )
        new_form_data = {
            'group': self.group1.id,
            'text': 'Другой тестовый пост',
            'image': uploaded1
        }
        response = self.authorized_client.post(reverse(
            'posts:post_edit', args=[post.id]),
            data=new_form_data,
            follow=True
        )
        self.assertEqual(
            response.context['post'].text, new_form_data['text'])

        self.assertEqual(
            response.context['post'].group.id, new_form_data['group'])
        self.assertEqual(
            response.context['post'].image, 'posts/small_new.gif')

    def test_redirect_guest(self):
        """Проверяем редирект гостя и колличество постов"""
        posts_count = Post.objects.count()
        response = self.guest_client.post(
            reverse('posts:post_create'))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertRedirects(
            response, '/auth/login/?next=/create/')

    def test_form_comment_guest(self):
        """Проверяем что гость не может отправлять форму комментария"""
        comment_count = Comment.objects.count()
        form_comment = {
            'text': 'Текст коментария'
        }
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_comment,
            follow=True
            )
        self.assertEqual(comment_count, Comment.objects.count())    
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.id}/comment/')