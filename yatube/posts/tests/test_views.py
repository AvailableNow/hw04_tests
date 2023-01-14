import shutil
import tempfile

from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User
from django.conf import settings

POSTS_SECOND_PAGE = 3
MAIN_URL = reverse('posts:index')
MAIN_PAGE_PAGINATOR_SECOND = MAIN_URL + '?page=2'

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
POST_TEST = "ш" * 50


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # cls.user = User.objects.create_user(username='testauthor')
        cls.group = Group.objects.create(
            title='Тестовая группа 1',
            slug='testslug_1',
            description='Тестовое описание 1',
        )

        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_slug_2',
            description='Тестовое описание 1',
        )

        cls.user = User.objects.create_user(username='testauthor_1')
        cls.username = cls.user.username

        cls.post = Post.objects.create(
            text=POST_TEST,
            group=cls.group,
            author=cls.user
        )
        # библиотека урлов
        cls.post_id = cls.post.id
        cls.POST_PAGE_URL = reverse(
            'posts:post_detail', args=[cls.post.id]
        )
        cls.GROUP_URL = reverse(
            'posts:group_list',
            args=[cls.group.slug]
        )
        cls.PROFILE_URL = reverse(
            'posts:profile',
            args=[cls.username]
        )
        cls.ANOTHER_GROUP_URL = reverse(
            'posts:group_list',
            args=[cls.group_2.slug]
        )

    # Удаляем временную папку
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # первый клиент автор поста
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_group_profile_show_correct_context(self):
        """Шаблоны index,group,profile сформированы с правильным контекстом."""
        urls = {
            MAIN_URL: 'page_obj',
            self.GROUP_URL: 'page_obj',
            self.PROFILE_URL: 'page_obj',
            self.POST_PAGE_URL: 'post',
        }
        for url, context_name in urls.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                if context_name == 'page_obj':
                    self.assertEqual(len(response.context.get('page_obj')), 1)
                    chek_post = response.context.get('page_obj')[0]
                else:
                    chek_post = response.context['post']
                    self.assertEqual(POST_TEST, chek_post.text)
                    self.assertEqual(self.post.author, chek_post.author)
                    self.assertEqual(self.post.group, chek_post.group)
                    self.assertEqual(self.post, chek_post)

    def test_profile_has_correct_context(self):
        '''Автор в контексте Профиля'''
        response = self.authorized_client.get(self.PROFILE_URL)
        self.assertEqual(
            response.context['author'], self.user
        )

    def test_group_list_has_correct_context(self):
        '''Группа в контексте Групп-ленты без искажения атрибутов'''
        response = self.authorized_client.get(self.GROUP_URL)
        group = response.context['group']
        self.assertEqual(group.title, self.group.title)
        self.assertEqual(group.description, self.group.description)
        self.assertEqual(group.slug, self.group.slug)
        self.assertEqual(group.pk, self.group.pk)

    def test_post_to_the_right_group(self):
        '''Пост не попал на чужую Групп-ленту'''
        response = self.authorized_client.get(self.ANOTHER_GROUP_URL)
        self.assertNotIn(self.post, response.context['page_obj'])


class PaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='SomeUsername')
        cls.group_3 = Group.objects.create(
            title='Тестовый заголовок',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.bulk_create(
            [
                Post(
                    text=f"Тестовый текст{i}",
                    author=cls.user,
                    group=cls.group_3
                )
                for i in range(settings.MAX_POSTS + POSTS_SECOND_PAGE)
            ]
        )
        cls.guest = Client()
        cls.GROUP_URL = reverse("posts:group_list", args=[cls.group_3.slug])
        cls.GROUP_LIST_PAGINATOR_SECOND = f'{cls.GROUP_URL}?page=2'
        cls.PROFILE_PAGE = reverse("posts:profile", args=[cls.user.username])
        cls.PROFILE_PAGINATOR_SECOND = f'{cls.PROFILE_PAGE}?page=2'

    def test_paginator(self):

        urls = {
            MAIN_URL: settings.MAX_POSTS,
            MAIN_PAGE_PAGINATOR_SECOND: POSTS_SECOND_PAGE,
            self.GROUP_URL: settings.MAX_POSTS,
            self.GROUP_LIST_PAGINATOR_SECOND: POSTS_SECOND_PAGE,
            self.PROFILE_PAGE: settings.MAX_POSTS,
            self.PROFILE_PAGINATOR_SECOND: POSTS_SECOND_PAGE,
        }
        for url, number in urls.items():
            with self.subTest(url=url):
                response = self.guest.get(url)
                self.assertEqual(
                    len(response.context['page_obj']), number
                )
