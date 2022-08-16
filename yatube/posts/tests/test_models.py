from django.contrib.auth import get_user_model
from django.test import TestCase
from posts import constants

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='TestGroup',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост размером более 15 символов',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        test_post = PostModelTest.post
        expected = test_post.text[:constants.str_length]
        self.assertEqual(expected, str(test_post))


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='TestGroup',
            slug='test-slug',
            description='Тестовое описание',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        test_group = GroupModelTest.group
        expected = test_group.title
        self.assertEqual(expected, str(test_group))
