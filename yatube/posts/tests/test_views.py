import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post, Follow

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='TestGroup',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            text='TestText',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            'posts/index.html': reverse(
                'posts:home_page'
            ),
            'posts/group_list.html': reverse(
                'posts:group_posts',
                kwargs={'slug': self.group.slug}
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': self.post.author}
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ),
            'posts/create_post.html': reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            )

        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def context_test(self, post):
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.id, self.post.id)
        self.assertEqual(post.image, self.post.image)

    def test_home_page_show_correct_context(self):
        """Проверяем контекст home_page"""
        response = self.authorized_client.get(
            reverse('posts:home_page')
        )
        self.assertIn('page_obj', response.context)
        post = response.context['page_obj'][0]
        self.context_test(post)

    def test_group_page_show_correct_context(self):
        """Проверяем контекст group_list"""
        response = self.authorized_client.get(
            reverse('posts:group_posts',
                    kwargs={'slug': self.group.slug})
        )
        self.assertIn('page_obj', response.context)
        post = response.context['page_obj'][0]
        group = response.context['group']
        self.assertEqual(group, self.group)
        self.context_test(post)

    def test_profile_page_show_correct_context(self):
        """Проверяем контекст profile"""
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.post.author})
        )
        self.assertIn('page_obj', response.context)
        post = response.context['page_obj'][0]
        author = response.context['author']
        self.assertEqual(author, self.post.author)
        self.context_test(post)

    def test_post_detail_page_show_correct_context(self):
        """Проверяем контекст post_detail"""
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id})
        )
        self.assertIn('post_list', response.context)
        post_list = response.context['post_list']
        post = response.context['post']
        self.assertEqual(post_list, 1)
        self.context_test(post)

    def test_create_post_page_show_correct_context(self):
        """Проверяем вывод формы create_post"""
        response = self.authorized_client.get(
            reverse('posts:post_create')
        )
        self.assertIn('form', response.context)
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get(
                    'form'
                ).fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_page_show_correct_context(self):
        """Проверяем вывод формы create_post при редактировании поста"""
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id})
        )
        self.assertIn('form', response.context)
        self.assertIn('is_edit', response.context)
        self.assertEqual(response.context['is_edit'], True)
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get(
                    'form'
                ).fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser2')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='TestGroup',
            slug='test-slug-2'
        )
        posts = []
        for p in range(13):
            posts.append(Post(
                author=cls.user,
                text='TestText',
                group=cls.group
            )
            )
        cls.post = Post.objects.bulk_create(posts)

    def setUp(self):
        cache.clear()

    def test_home_first_page_contains_ten_records(self):
        response = self.authorized_client.get(reverse('posts:home_page'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_home_second_page_contains_three_records(self):
        response = self.authorized_client.get(
            reverse('posts:home_page') + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_first_page_contains_ten_records(self):
        response = self.authorized_client.get(
            reverse('posts:group_posts',
                    kwargs={'slug': self.group.slug})
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_group_second_page_contains_three_records(self):
        response = self.authorized_client.get(
            reverse(
                'posts:group_posts',
                kwargs={'slug': self.group.slug}
            ) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_profile_first_page_contains_ten_records(self):
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user})
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile_second_page_contains_ten_records(self):
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user}
            ) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)


class PostCreateTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='TestUser3')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='TestGroup',
            slug='test-slug-3'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='TestText'
        )

    def setUp(self):
        self.another_group = Group.objects.create(
            title='SecondGroup',
            slug='second-slug'
        )

    def test_post_in_right_place(self):
        """Проверяем появление поста на страницах."""
        self.another_post = Post.objects.create(
            author=self.user,
            group=self.group,
            text='NewPost'
        )
        test_pages = {
            reverse('posts:home_page'),
            reverse(
                'posts:group_posts',
                kwargs={'slug': self.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': self.post.author}
            )
        }
        for url in test_pages:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                post = response.context['page_obj'][0]
                self.assertEqual(post, self.another_post)

    def test_that_post_not_in_another_group(self):
        """Проверяем отсутствие поста в другой группе."""
        response = self.authorized_client.get(
            reverse('posts:group_posts',
                    kwargs={'slug': self.another_group.slug})
        )
        self.assertEqual(len(response.context['page_obj']), 0)


class TestCache(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='HelloUser')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_home_page_20_sec_cache(self):
        self.post = Post.objects.create(
            author=self.user,
            text="HelloCache"
        )
        first_response = self.authorized_client.get(
            reverse('posts:home_page')
        )
        Post.objects.all().delete()
        second_response = self.authorized_client.get(
            reverse('posts:home_page')
        )
        self.assertEqual(
            first_response.content, second_response.content
        )


class TestFollow(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='TestUser')
        cls.post = Post.objects.create(
            author=cls.user,
            text='sometext'
        )
        cls.sec_user = User.objects.create(username='SecUser')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.sec_user)

    def test_that_user_can_follow_unfollow(self):
        response = self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user}
            )
        )
        self.assertRedirects(
            response,
            f'/profile/{self.user}/'
        )
        response = self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.user}
            )
        )
        self.assertRedirects(
            response,
            f'/profile/{self.user}/'
        )

    def test_that_posts_shows_only_for_followers(self):
        Follow.objects.create(
            user=self.sec_user,
            author=self.user
        )
        response_1 = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.authorized_client.force_login(self.user)
        response_2 = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertNotEqual(response_1.content, response_2.content)
