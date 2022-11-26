import shutil
import tempfile

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from ..models import Post, Group, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
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
            title='Тестовая группа1',
            slug='test-slug1',
            description='Тестовое описание1'
        )

        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def code_for_checking_post(self, post):
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.pub_date, self.post.pub_date)
        self.assertEqual(post.image, self.post.image)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            (reverse(
                'posts:profile', kwargs={
                    'username': self.user.username})): 'posts/profile.html',
            reverse(
                'posts:post_create'): 'posts/create_post.html',
            (reverse(
                'posts:post_edit', args=[
                    self.post.id])): 'posts/create_post.html',
            (reverse(
                'posts:post_detail', args=[
                    self.post.id])): 'posts/post_detail.html',
            (reverse(
                'posts:group_list', kwargs={
                    'slug': self.group.slug})): 'posts/group_list.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_context(self):
        """Шаблон index сформирован с правильным контекстом"""
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(
            len(response.context['page_obj']), 1, 'Пост не создан')
        post_object = response.context['page_obj'][0]
        self.code_for_checking_post(post_object)

    def test_profile_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username}))
        self.assertEqual(
            len(response.context['page_obj']), 1, 'Пост не создан')
        post_object = response.context['page_obj'][0]
        author_name = response.context['author']
        self.code_for_checking_post(post_object)
        self.assertEqual(author_name, self.user)

    def test_post_detail_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        self.assertEqual(
            response.context['post'].text, self.post.text)
        self.assertEqual(
            response.context['post'].author.username,
            self.user.username
        )
        self.assertEqual(response.context['post'].image, self.post.image)
        self.assertEqual(response.context['post'], self.post)

    def test_group_posts_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}))
        self.assertEqual(
            len(response.context['page_obj']), 1, 'Пост не создан')
        post_object = response.context['page_obj'][0]
        group_object = response.context['group']
        self.code_for_checking_post(post_object)
        self.assertEqual(group_object, self.group)
        self.assertEqual(post_object.group, self.post.group)

    def test_post_create_context(self):
        """ Шаблон create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))

        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_fields = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_fields, expected)

    def test_post_edit_context(self):
        """ Шаблон edit для create сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={
                'post_id': self.post.id}))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_fields = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_fields, expected)

    def test_new_post_in_group(self):
        """Пост сохраняется в группе."""
        posts_count = Post.objects.filter(group=self.group).count()
        Post.objects.create(
            text='Тестовый текст для нового поста',
            author=self.user,
            group=self.group,
        )
        self.assertNotEqual(Post.objects.filter(
            group=self.group).count(), posts_count
        )

    def test_new_post_not_in_another_group(self):
        """Пост не сохраняется в группе, не предназначенный для нее."""
        posts_count = Post.objects.filter(group=self.group1).count()
        Post.objects.create(
            text='Тестовый текст для нового поста',
            author=self.user,
            group=self.group,
        )
        self.assertEqual(Post.objects.filter(
            group=self.group1).count(), posts_count
        )