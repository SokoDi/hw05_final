from django.test import TestCase, Client
from http import HTTPStatus

from posts.models import Post, Group, User


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='author')
        cls.user1 = User.objects.create(username='non_author')
        cls.group = Group.objects.create(
            title='Тестовое название',
            slug='test-slug',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client1 = Client()
        self.authorized_client1.force_login(self.user1)

    def test_site_access_site(self):
        """Проверяем доступность к страницам для гостей."""
        pages_being_checked = (
            '/',
            f'/profile/{self.user.username}/',
            '/group/test-slug/',
            f'/posts/{self.post.id}/'
        )
        for adres in pages_being_checked:
            with self.subTest(adres=adres):
                response = self.guest_client.get(adres)
                error_name = f'Ошибка: нет доступа к странице {adres}'
                self.assertEqual(
                    response.status_code, HTTPStatus.OK, error_name)

    def test_authorized_user_of_the_site(self):
        """Проверяем доступность к страницам
        для авторизированного пользывателя."""
        pages_being_checked = [
            '/',
            f'/profile/{self.user.username}/',
            '/group/test-slug/',
            f'/posts/{self.post.id}/',
            '/create/',
        ]
        for adres in pages_being_checked:
            with self.subTest(adres=adres):
                response = self.authorized_client.get(adres)
                error_name = f'Ошибка: нет доступа к странице {adres}'
                self.assertEqual(
                    response.status_code, HTTPStatus.OK, error_name)

    def test_page_edits_post(self):
        """Порверка доступа к странице редактирования поста"""
        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_transference_user(self):
        """Проверка перенаправления гостя"""
        redirect = {
            '/create/',
            f'/posts/{self.post.id}/edit/'
        }
        for adres in redirect:
            with self.subTest(adres=adres):
                response = self.guest_client.get(adres, follow=True)
                error_name = f'Ошибка: нет доступа к странице {adres}'
                self.assertEqual(
                    response.status_code, HTTPStatus.OK, error_name)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                error_name = f'Ошибка: нет доступа к странице {template}'
                self.assertTemplateUsed(response, template, error_name)

    def test_urls_post_edit_not_author(self):
        """Проверка перенаправления страницы редактирования
        пользователя не являющегося автором поста """
        response = self.authorized_client1.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
