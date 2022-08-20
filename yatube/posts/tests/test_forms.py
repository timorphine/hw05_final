import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateForm(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='TestUser')
        cls.group = Group.objects.create(
            title='TestGroup',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='TestText'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_authorized_user_can_make_post(self):
        """Проверяем возможность создания поста авторизованным пользователем"""
        obj_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        post_form = {
            'group': self.group.id,
            'text': 'AnotherText',
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=post_form,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': self.user}
            )
        )
        self.assertEqual(Post.objects.count(), obj_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=post_form['text'],
                group=self.group,
                image='posts/small.gif'
            ).exists()
        )
        last_post = Post.objects.first()
        self.assertEqual(last_post.text, post_form['text'])
        self.assertEqual(last_post.group, self.post.group)
        self.assertEqual(last_post.author, self.post.author)

    def test_edit_post(self):
        """Проверяем изменение поста в БД после редакции"""
        obj_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='smallest.gif',
            content=small_gif,
            content_type='image/gif'
        )
        changed_post_form = {
            'group': self.group.id,
            'text': 'OneMoreText',
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ),
            data=changed_post_form,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )
        self.assertEqual(Post.objects.count(), obj_count)
        self.assertTrue(
            Post.objects.filter(
                id=self.post.id,
                image='posts/smallest.gif'
            ).exists()
        )
        changed_post = Post.objects.get(id=self.post.id)
        self.assertEqual(changed_post.text, changed_post_form['text'])
        self.assertEqual(changed_post.group, self.post.group)
        self.assertEqual(changed_post.author, self.post.author)


class CommentCreateForm(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Vasya')
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)
        cls.group = Group.objects.create(
            title='NewGroup',
            slug='new-group'
        )
        cls.post = Post.objects.create(
            text='NewPost',
            author=cls.user,
            group=cls.group
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            text='NewComment',
            author=cls.user
        )

    def test_comments_are_only_for_authorized_users(self):
        """Коммент от неавторизованного юзера вызывает редирект."""
        obj_count = Comment.objects.count()
        self.guest_client = Client()
        comment_form = {
            'text': 'Privet'
        }
        response = self.guest_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.id}
            ),
            data=comment_form,
            follow=True
        )
        self.assertRedirects(
            response,
            '/auth/login/?next=/posts/1/comment/'
        )
        self.assertEqual(obj_count, 1)

    def test_authorized_user_can_comment(self):
        """Проверяем появление коммента на странице"""
        obj_count = Comment.objects.count()
        comment_form = {
            'text': 'NewComment'
        }
        response = self.authorized_user.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.id}
            ),
            data=comment_form,
            follow=True
        )
        self.assertRedirects(
            response,
            f'/posts/{self.post.id}/'
        )
        self.assertEqual(Comment.objects.count(), obj_count + 1)
