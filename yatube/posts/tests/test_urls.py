from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from posts.models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Author')
        cls.not_author = User.objects.create_user(username='not_author')
        cls.group = Group.objects.create(
            title='TestGroup',
            slug='Test-slug'
        )
        cls.post = Post.objects.create(
            text='TestPost',
            group=cls.group,
            author=cls.user
        )

    def setUp(self):
        cache.clear()
        self.autorized_client = Client()
        self.autorized_client.force_login(self.user)
        self.not_author_client = Client()
        self.not_author_client.force_login(self.not_author)

    def test_page_responses_for_authorized(self):
        urls = {
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.user}/',
            f'/posts/{self.post.id}/',
            '/create/'
        }
        for url in urls:
            with self.subTest(url=url):
                response = self.not_author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page_response(self):
        """Тест ответа несуществующей страницы."""
        response = self.client.get('/unexisted_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_create_page_for_not_auth(self):
        """Тест редиректа со страницы create для неавторизованного юзера."""
        response = self.client.get('/create/')
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_post_edit_for_guest(self):
        self.guest_client = Client()
        response = self.guest_client.get(
            f'/posts/{self.post.id}/edit/'
        )
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{self.post.id}/edit/'
        )

    def test_edit_for_non_author(self):
        """Редактирование поста доступно только для автора."""
        response = self.not_author_client.get(
            f'/posts/{self.post.id}/edit/'
        )
        self.assertRedirects(
            response, f'/profile/{self.not_author}/')

    def test_urls_leads_to_right_templates(self):
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.not_author}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html'
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.autorized_client.get(address)
                self.assertTemplateUsed(response, template)


class TestErrorCustomPages(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='HiThere')
        cls.post = Post.objects.create(
            author=cls.user,
            text='HowAreU'
        )

    def setUp(self):
        self.guest_client = Client()

    def test_404_page_uses_custom_template(self):
        response = self.guest_client.get(
            '/unexisted/'
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
