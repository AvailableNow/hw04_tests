from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User

MAIN_URL = reverse('posts:index')
NEW_POST_URL = reverse('posts:post_create')
NOT_FOUND_URL = '/unexisting-page/'
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

    def setUp(self):
        # первый клиент автор поста
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.username = self.user.username
        # второй клиент не автор поста
        self.authorized_client_2 = Client()
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)

        self.slug = self.group.slug
        self.GROUP_URL = reverse("posts:group_list", args=[self.slug])
        self.PROFILE_URL = reverse("posts:profile", args=[self.username])

    # 1. Проверка запросов к страницам
    def test_url_exists(self):
        """Проверка доступности адресов любого клиента"""
        url_names = [
            [MAIN_URL, self.guest_client, 200],
            [MAIN_URL, self.authorized_client, 200],
            [self.GROUP_URL, self.guest_client, 200],
            [self.PROFILE_URL, self.guest_client, 200],
            [NEW_POST_URL, self.guest_client, 302],
            [NEW_POST_URL, self.authorized_client, 200],
            [self.POST_PAGE_URL, self.guest_client, 200],
            [self.EDIT_POST_URL, self.guest_client, 302],
            [self.EDIT_POST_URL, self.authorized_client, 200],
            [NOT_FOUND_URL, self.guest_client, 404],
            [NOT_FOUND_URL, self.authorized_client, 404],
        ]

        for url, client, code in url_names:
            with self.subTest(url=url):
                self.assertEqual(client.get(url).status_code, code)

    # 2. Проверка шаблонов
    def test_url_uses_correct_templates(self):
        """Проверка шаблонов для адресов и разных клиентов "/" """
        url_names = [
            ["posts/index.html", MAIN_URL, self.guest_client],
            ["posts/group_list.html", self.GROUP_URL, self.guest_client],
            ["posts/post_detail.html", self.POST_PAGE_URL, self.guest_client],
            ["posts/profile.html", self.PROFILE_URL, self.guest_client],
            ["posts/create_post.html", NEW_POST_URL, self.authorized_client],
            ["posts/create_post.html", self.EDIT_POST_URL,
             self.authorized_client],
        ]

        for template, url, client in url_names:
            with self.subTest(url=url):
                self.assertTemplateUsed(client.get(url), template)

    # Проверка редиректов
    def test_redirect(self):
        """Проверка редиректов для страниц."""
        url_names = [
            [NEW_POST_URL, self.guest_client, (reverse("login") + "?next="
                                               + NEW_POST_URL)],
            [self.EDIT_POST_URL, self.guest_client, (reverse("login")
                                                     + "?next="
                                                     + self.EDIT_POST_URL)],
            [self.EDIT_POST_URL, self.authorized_client_2, self.PROFILE_URL],
        ]

        for url, client, redirected in url_names:
            with self.subTest(url=url):
                self.assertRedirects(client.get(url, follow=True), redirected)
