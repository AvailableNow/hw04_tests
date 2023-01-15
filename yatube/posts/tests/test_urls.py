from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User

MAIN_URL = reverse('posts:index')
NEW_POST_URL = reverse('posts:post_create')
NOT_FOUND_URL = '/unexisting-page/'
GROUP_URL = reverse(
    'posts:group_list',
    args=['test_slug']
)
PROFILE_URL = reverse(
    'posts:profile',
    args=['testauthor_1']
)
POST_TEXT = "ш" * 50


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # создание пользователей
        cls.user = User.objects.create_user(username='testauthor_1')
        cls.user_2 = User.objects.create_user(username="testauthor_2")
        # создание группы
        cls.group = Group.objects.create(
            title="Тест-название",
            slug="test_slug",
            description="Тест-описание"
        )
        # создание поста
        cls.post = Post.objects.create(
            text=POST_TEXT,
            group=cls.group,
            author=cls.user
        )
        # библиотека урлов
        cls.POST_PAGE_URL = reverse(
            'posts:post_detail',
            args=[cls.post.id]
        )
        cls.EDIT_POST_URL = reverse(
            'posts:post_edit',
            args=[cls.post.id]
        )
        cls.POST_EDIT_REDIRECT = reverse(
            "login") + "?next=" + cls.EDIT_POST_URL
        cls.CREATE_REDIRECT = reverse(
            "login") + "?next=" + NEW_POST_URL

    def setUp(self):
        # первый клиент автор поста
        self.guest = Client()
        self.author = Client()
        self.author.force_login(self.user)
        # второй клиент не автор поста
        self.another = Client()
        self.another.force_login(self.user_2)

    # 1. Проверка запросов к страницам
    def test_url_exists(self):
        """Проверка доступности адресов любого клиента"""
        cases = [
            [MAIN_URL, self.guest, 200],
            [GROUP_URL, self.guest, 200],
            [PROFILE_URL, self.guest, 200],
            [NEW_POST_URL, self.guest, 302],
            [NEW_POST_URL, self.author, 200],
            [self.POST_PAGE_URL, self.guest, 200],
            [self.EDIT_POST_URL, self.guest, 302],
            [self.EDIT_POST_URL, self.author, 200],
            [NOT_FOUND_URL, self.guest, 404],
            [self.EDIT_POST_URL, self.another, 302],
        ]
        for url, client, code in cases:
            with self.subTest(url=url, client=client):
                self.assertEqual(client.get(url).status_code, code)

    # 2. Проверка шаблонов
    def test_url_uses_correct_templates(self):
        """Проверка шаблонов для адресов и разных клиентов "/" """
        url_names = [
            ["posts/index.html", MAIN_URL, self.guest],
            ["posts/group_list.html", GROUP_URL, self.guest],
            ["posts/post_detail.html", self.POST_PAGE_URL, self.guest],
            ["posts/profile.html", PROFILE_URL, self.guest],
            ["posts/create_post.html", NEW_POST_URL, self.author],
            ["posts/create_post.html", self.EDIT_POST_URL,
             self.author],
        ]
        for template, url, client in url_names:
            with self.subTest(url=url):
                self.assertTemplateUsed(client.get(url), template)

    # Проверка редиректов
    def test_redirect(self):
        """Проверка редиректов для страниц."""
        url_names = [
            [NEW_POST_URL, self.guest, self.CREATE_REDIRECT],
            [self.EDIT_POST_URL, self.guest,
                self.POST_EDIT_REDIRECT],
            [self.EDIT_POST_URL, self.another, PROFILE_URL],
        ]
        for url, client, redirected in url_names:
            with self.subTest(url=url, client=client):
                self.assertRedirects(client.get(url, follow=True), redirected)
