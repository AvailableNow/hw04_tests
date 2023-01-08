from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User

MAIN_PAGE = reverse('posts:index')
NEW_POST = reverse('posts:post_create')
PAGE_NOT_FOUND = '/unexisting-page/'
POST_TEXT = "ш" * 50


class StaticURLTests(TestCase):
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
        # библиотека урлов
        # self.post_id = self.post.pk
        self.POST_PAGE = reverse('posts:post_detail', args=[self.post.id])
        self.EDIT_PAGE = reverse("posts:post_edit",
                                 args=[self.post.id])

    # 1. Проверка запросов к страницам
    def test_url_exists(self):
        """Проверка доступности адресов любого клиента"""
        slug = self.group.slug
        GROUP_PAGE = reverse("posts:group_list", args=[slug])
        PROFILE_PAGE = reverse("posts:profile", args=[self.username])
        url_names = [
            [MAIN_PAGE, self.guest_client, 200],
            [GROUP_PAGE, self.guest_client, 200],
            [PROFILE_PAGE, self.guest_client, 200],
            [NEW_POST, self.guest_client, 302],
            [NEW_POST, self.authorized_client, 200],
            [self.POST_PAGE, self.guest_client, 200],
            [self.EDIT_PAGE, self.guest_client, 302],
            [self.EDIT_PAGE, self.authorized_client, 200],
            [PAGE_NOT_FOUND, self.guest_client, 404],
        ]

        for url, client, code in url_names:
            with self.subTest(url=url):
                self.assertEqual(client.get(url).status_code, code)

    # 2. Проверка шаблонов
    def test_url_uses_correct_templates(self):
        """Проверка шаблонов для адресов и разных клиентов "/" """
        slug = self.group.slug
        GROUP_PAGE = reverse("posts:group_list", args=[slug])
        PROFILE_PAGE = reverse("posts:profile", args=[self.username])
        url_names = [
            ["posts/index.html", MAIN_PAGE, self.guest_client],
            ["posts/group_list.html", GROUP_PAGE, self.guest_client],
            ["posts/post_detail.html", self.POST_PAGE, self.guest_client],
            ["posts/profile.html", PROFILE_PAGE, self.guest_client],
            ["posts/create_post.html", NEW_POST, self.authorized_client],
            ["posts/create_post.html", self.EDIT_PAGE, self.authorized_client],
        ]

        for template, url, client in url_names:
            with self.subTest(url=url):
                self.assertTemplateUsed(client.get(url), template)

    # Проверка редиректов
    def test_redirect(self):
        """Проверка редиректов для страниц."""
        PROFILE_PAGE = reverse("posts:profile", args=[self.username])
        url_names = [
            [NEW_POST, self.guest_client, (reverse("login") + "?next="
                                           + NEW_POST)],
            [self.EDIT_PAGE, self.guest_client, (reverse("login")
                                                 + "?next=" + self.EDIT_PAGE)],
            [self.EDIT_PAGE, self.authorized_client_2, PROFILE_PAGE],
        ]

        for url, client, redirected in url_names:
            with self.subTest(url=url):
                self.assertRedirects(client.get(url, follow=True), redirected)
