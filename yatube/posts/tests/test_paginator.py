from django.test import Client, TestCase
from django.urls import reverse
from django.conf import settings

from ..models import Post, Group, Follow, User


class PaginatorViewsTest(TestCase):

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='author')
        self.user1 = User.objects.create_user(username='not_author')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client1 = Client()
        self.authorized_client1.force_login(self.user1)
        self.group = Group.objects.create(title='Тестовая группа',
                                          slug='test_group')
        self.follow = Follow.objects.create(
            author=self.user,
            user=self.user1
        )
        bilk_post: list = []
        for i in range(settings.TEST_OF_POST):
            bilk_post.append(
                Post(text=f'Тестовый текст {i}',
                     group=self.group,
                     author=self.user))
        Post.objects.bulk_create(bilk_post)
        self.pages: tuple = (reverse('posts:index'),
                        reverse('posts:profile',
                                kwargs={'username': self.user.username}),
                        reverse('posts:group_list',
                                kwargs={'slug': self.group.slug}))


    def test_correct_page_context_guest_client(self):
        """Проверка количества постов на
         первой и второй страницах для гостя."""
        for page in self.pages:
            response1 = self.guest_client.get(page)
            response2 = self.guest_client.get(page + '?page=2')
            count_posts1 = len(response1.context['page_obj'])
            count_posts2 = len(response2.context['page_obj'])
            self.assertEqual(count_posts1, settings.POSTS_PER_PAGE)
            self.assertEqual(
                count_posts2, settings.TEST_OF_POST - settings.POSTS_PER_PAGE)

    def test_correct_page_context_authorized_client(self):
        """Проверка количества постов
        на первой и второй страницах для юзера. """
        for page in self.pages:
            response1 = self.authorized_client.get(page)
            response2 = self.authorized_client.get(page + '?page=2')
            count_posts1 = len(response1.context['page_obj'])
            count_posts2 = len(response2.context['page_obj'])
            self.assertEqual(count_posts1, settings.POSTS_PER_PAGE)
            self.assertEqual(
                count_posts2, settings.TEST_OF_POST - settings.POSTS_PER_PAGE)

    def test_correct_page_follow(self):
        """Проверка количества постов
        на первой и второй страницах подписак."""
        pages: tuple = (reverse('posts:follow_index'),
                        reverse('posts:profile',
                                kwargs={'username': self.user.username})
        )
        for page in pages:
            response1 = self.authorized_client1.get(page)
            response2 = self.authorized_client1.get(page + '?page=2')
            count_posts1 = len(response1.context['page_obj'])
            count_posts2 = len(response2.context['page_obj'])
            self.assertEqual(count_posts1, settings.POSTS_PER_PAGE)
            self.assertEqual(
                count_posts2, settings.TEST_OF_POST - settings.POSTS_PER_PAGE)


