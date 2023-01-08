import shutil
import tempfile
from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User

MAIN_PAGE = reverse('posts:index')
NEW_POST = reverse('posts:post_create')
PAGE_NOT_FOUND = '/unexisting-page/'

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
POST_TEST = "ш" * 50


class GroupPostTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # cls.user = User.objects.create_user(username='testauthor')
        cls.group = Group.objects.create(
            title='Тестовая группа 1',
            slug='testslug_1',
            description='Тестовое описание 1',
        )

    # Удаляем временную папку
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # первый клиент автор поста
        self.guest_client = Client()
        self.user = User.objects.create_user(username='testauthor_1')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.username = self.user.username
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.post = Post.objects.create(
            text=POST_TEST,
            group=self.group,
            author=self.user
        )

        # библиотека урлов
        self.post_id = self.post.id
        self.slug = self.group.slug
        self.GROUP_PAGE = reverse("posts:group_list", args=[self.slug])
        self.PROFILE_PAGE = reverse("posts:profile", args=[self.username])
        self.POST_PAGE = reverse(
            'posts:post_detail', args=[self.post.id]
        )
        self.EDIT_PAGE = reverse(
            'posts:post_edit', args=[self.post.id]
        )

    def test_index_group_profile_show_correct_context(self):
        """Шаблоны index,group,profile сформированы с правильным контекстом."""
        urls = [MAIN_PAGE, self.GROUP_PAGE, self.PROFILE_PAGE, ]

        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                post = response.context['page_obj'][0]
                self.assertEqual(Post.objects.count(), 1)
                self.assertEqual(POST_TEST, post.text)
                self.assertEqual(self.username, post.author.username)
                self.assertEqual(self.group.title, post.group.title)

    def test_post_show_correct_context(self):
        """Страница post сформирована с правильным контекстом."""
        url = self.POST_PAGE
        response = self.guest_client.get(url)
        post = response.context['post']
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(POST_TEST, post.text)
        self.assertEqual(self.username, post.author.username)
        self.assertEqual(self.group.title, post.group.title)
        self.assertEqual(self.group.title, post.group.title)
