import shutil
import tempfile

from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post, User

# Создаем временную папку для медиа-файлов;
# на момент теста медиа папка будет переопределена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
POST_TEST = "ш" * 50

MAIN_PAGE = reverse('posts:index')
NEW_POST = reverse('posts:post_create')


# Для сохранения media-файлов в тестах будет использоватьсяgs
# временная папка TEMP_MEDIA_ROOT, а потом мы ее удалим
@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем записи в базе данных
        cls.user = User.objects.create(username="NoNoName")
        cls.form = PostForm()
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
            author=cls.user,
            text="Тестовый пост",
            group=cls.group,
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

        # второй клиент не автор поста
        self.authorized_client_2 = Client()
        self.user_2 = User.objects.create_user(username='testauthor_2')
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)
        self.username_2 = self.user_2.username

        self.post = Post.objects.create(
            text=POST_TEST,
            group=self.group,
            author=self.user
        )
        self.EDIT_PAGE = reverse(
            'posts:post_edit', args=[self.post.id]
        )

    # Тест для проверки формы создания нового поста (create_post)
    def test_create_post(self):
        """Проверка, что валидная форма создаёт пост"""
        # Подготавливаем данные для передачи в форму
        form_data = {
            "text": "тестовая публикация",
            "group": self.group.pk
        }
        # Передаем данные в нашу форму
        form = PostForm(form_data)
        #  Проверяем заполнение формы
        self.assertTrue(form.is_valid())

        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()
        # Отправляем POST-запрос (сохраняем наш пост)
        self.authorized_client.post(
            NEW_POST,
            data=form_data,
            folow=True
        )
        # Сравниваем пост с полями формы
        post_object = Post.objects.filter(
            text=form_data['text'],
            group=form_data['group'],
            author=self.user.pk
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(post_object.exists)

    def test_post_edit_by_author(self):
        '''Выполнение редактирование поста автором'''
        pk_list_before = Post.objects.filter().values_list('pk', flat=True)
        # Подготавливаем данные для передачи в форму
        form_data = {
            'text': 'Автор, редактирует пост',
            'group': self.group_2.pk,
        }
        # Отправляем POST-запрос (редактируем наш пост)
        self.authorized_client.post(
            self.EDIT_PAGE,
            data=form_data,
            follow=False
        )

        pk_list_after = Post.objects.filter().values_list('pk', flat=True)
        self.assertEqual(set(pk_list_before), set(pk_list_after))
        new_post = Post.objects.get(pk=self.post.id)
        self.assertEqual(new_post.text, form_data['text'])
        self.assertEqual(new_post.group.pk, form_data['group'])
        self.assertEqual(new_post.author.username, self.username)

    def test_post_edit_by_non_author(self):
        '''Редактирование поста не автором поста
        невозможно'''
        pk_list_before = Post.objects.filter().values_list('pk', flat=True)

        form_data = {
            'text': 'это сообщение не должно переписаться в пост',
            'group': self.group_2.pk,
        }
        self.authorized_client_2.post(
            self.EDIT_PAGE,
            data=form_data,
            follow=False
        )

        pk_list_after = Post.objects.filter().values_list('pk', flat=True)
        self.assertEqual(set(pk_list_before), set(pk_list_after))
        new_post = Post.objects.get(pk=pk_list_after[-0])
        self.assertEqual(new_post.text, self.post.text)
        self.assertEqual(new_post.group.pk, self.post.group.pk)
        self.assertEqual(new_post.author.username, self.username)
