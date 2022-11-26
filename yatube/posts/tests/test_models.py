from django.test import TestCase
from django.conf import settings

from posts.models import Post, Group, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст поста'
        )
        cls.group = Group.objects.create(
            title='Тестовое название',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        expected_object_name = self.post.text[
            :settings.FIRST_TEXT_CHARACTERS_POST]
        self.assertEqual(expected_object_name, str(self.post))

    def test_str_name_group(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        expected_object_name = self.group.title
        self.assertEqual(expected_object_name, str(self.group))
