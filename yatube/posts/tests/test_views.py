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
        self.username = self.user.username
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_group_profile_show_correct_context(self):
        """Шаблоны index,group,profile сформированы с правильным контекстом."""
        slug = self.group.slug
        GROUP_URL = reverse("posts:group_list", args=[slug])
        PROFILE_URL = reverse("posts:profile", args=[self.username])
        urls = {
            MAIN_URL: 'page_obj',
            GROUP_URL: 'page_obj',
            PROFILE_URL: 'page_obj',
            self.POST_PAGE_URL: 'post',
        }
        for url, context_name in urls.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                if context_name == 'page_obj':
                    post_list = response.context['page_obj']
                    self.assertEqual(len(post_list), 1)
                    post = post_list[0]
                else:
                    post = response.context['post']
                    self.assertEqual(Post.objects.count(), 1)
                    self.assertEqual(POST_TEST, post.text)
                    self.assertEqual(self.username, post.author.username)
                    self.assertEqual(self.group.title, post.group.title)
                    self.assertEqual(self.post.id, post.id)

    def test_profile_has_correct_context(self):
        '''Автор в контексте Профиля'''
        PROFILE_URL = reverse("posts:profile", args=[self.username])
        response = self.authorized_client.get(PROFILE_URL)
        self.assertEqual(
            response.context['author'].username, self.user.username
        )

    def test_group_list_has_correct_context(self):
        '''Группа в контексте Групп-ленты без искажения атрибутов'''
        slug = self.group.slug
        GROUP_URL = reverse("posts:group_list", args=[slug])
        response = self.authorized_client.get(GROUP_URL)
        group = response.context['group']
        self.assertEqual(group.title, self.group.title)
        self.assertEqual(group.description, self.group.description)
        self.assertEqual(group.slug, self.group.slug)
        self.assertEqual(group.pk, self.group.pk)

    def test_post_to_the_right_group(self):
        '''Пост не попал на чужую Групп-ленту'''
        self.slug = self.group_2.slug
        ANOTHER_GROUP_URL = reverse(
            'posts:group_list', args=[self.slug]
        )
        response = self.authorized_client.get(ANOTHER_GROUP_URL)
        group_posts = response.context['page_obj']
        self.assertNotIn(self.post, group_posts)


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

        cls.posts = []
        for i in range(settings.MAX_POSTS + POSTS_SECOND_PAGE):
            cls.posts.append(Post(
                text=f'Тестовый псто {i}',
                author=cls.user,
                group=cls.group_3,
            ))
        Post.objects.bulk_create(cls.posts)

        cls.guest = Client()

    def test_paginator(self):
        self.slug = self.group_3.slug
        GROUP_URL = reverse("posts:group_list", args=[self.slug])
        GROUP_LIST_PAGINATOR_SECOND = f'{GROUP_URL}?page=2'
        PROFILE_PAGE = reverse("posts:profile", args=[self.user.username])
        PROFILE_PAGINATOR_SECOND = f'{PROFILE_PAGE}?page=2'
        urls = {
            MAIN_URL: settings.MAX_POSTS,
            MAIN_PAGE_PAGINATOR_SECOND: POSTS_SECOND_PAGE,
            GROUP_URL: settings.MAX_POSTS,
            GROUP_LIST_PAGINATOR_SECOND: POSTS_SECOND_PAGE,
            PROFILE_PAGE: settings.MAX_POSTS,
            PROFILE_PAGINATOR_SECOND: POSTS_SECOND_PAGE,
        }
        for url, number in urls.items():
            with self.subTest(url=url):
                response = self.guest.get(url)
                self.assertEqual(
                    len(response.context['page_obj']), number
                )
