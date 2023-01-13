import shutil
import tempfile

from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post, User

# Создаем временную папку для медиа-файлов;
# на момент теста медиа папка будет переопределена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
POST_TEST = "ш" * 50

NEW_POST_URL = reverse('posts:post_create')


# Для сохранения media-файлов в тестах будет использоватьсяgs
# временная папка TEMP_MEDIA_ROOT, а потом мы ее удалим
@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем записи в базе данных
        cls.user = User.objects.create_user(username='testauthor_1')
        cls.user_2 = User.objects.create_user(username="testauthor_2")
        cls.group = Group.objects.create(
            title="Тестовый заголовок группы",
            slug="test-slug",
            description="Тестовое описание",
        )
        cls.group_2 = Group.objects.create(
            title="новая группа",
            slug='test_slug2',
            description="Тест-описание2"
        )

        # Создадим запись в БД
        cls.post = Post.objects.create(
            text=POST_TEST,
            group=cls.group,
            author=cls.user
        )

        cls.POST_PAGE_URL = reverse(
            'posts:post_detail',
            args=[cls.post.id]
        )
        cls.EDIT_POST_URL = reverse(
            'posts:post_edit',
            args=[cls.post.id]
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
        # второй клиент не автор поста
        self.authorized_client_2 = Client()
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)
        self.username_2 = self.user_2.username

        self.EDIT_POST_URL = reverse(
            'posts:post_edit', args=[self.post.id]
        )
        self.PROFILE_PAGE = reverse("posts:profile", args=[self.username])

    # Тест для проверки формы создания нового поста (create_post)
    def test_create_post(self):
        """Проверка, что валидная форма создаёт пост"""
        form_data = {
            "text": "тестовая публикация",
            "group": self.group.pk
        }

        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()

        posts_before = set(Post.objects.all())
        response = self.authorized_client.post(
            NEW_POST_URL,
            data=form_data,
            follow=True
        )
        posts_after = set(Post.objects.all())
        new_post_list = list(posts_after.difference(posts_before))
        new_post = new_post_list[0]
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(len(new_post_list), 1)
        self.assertEqual(new_post.text, form_data['text'])
        self.assertEqual(new_post.group.id, form_data['group'])
        self.assertEqual(new_post.author, self.user)
        self.assertRedirects(response, self.PROFILE_PAGE)

    def test_post_edit_by_author(self):
        '''Выполнение редактирование поста автором'''
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Автор, редактирует пост',
            'group': self.group_2.pk,
        }
        response = self.authorized_client.post(
            self.EDIT_POST_URL,
            data=form_data,
            follow=True
        )
        edited_post = Post.objects.get(pk=self.post.pk)
        self.assertRedirects(response, self.POST_PAGE_URL)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(edited_post.group.id, form_data['group'])
        self.assertEqual(edited_post.text, form_data['text'])
        # self.assertEqual(edited_post.author, self.post.author.username)

    def test_post_edit_by_non_author(self):
        '''Редактирование поста не автором поста
        невозможно'''
        form_data = {
            'text': 'это сообщение не должно переписаться в пост',
            'group': self.group.pk,
        }
        response = self.authorized_client_2.post(
            self.EDIT_POST_URL,
            data=form_data,
            follow=True
        )

        edited_post = Post.objects.get(pk=self.post.pk)
        self.assertRedirects(response, self.PROFILE_PAGE)
        self.assertEqual(edited_post.text, self.post.text)
        self.assertEqual(edited_post.group, self.post.group)
        self.assertEqual(edited_post.author, self.post.author)
