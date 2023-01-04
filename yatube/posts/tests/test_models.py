from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            pub_date='12262022',
            group=cls.group,
            text='Тестовый пост',
        )

    def test_verbose_name(self):
        task_post = PostModelTest.post
        task_group = PostModelTest.group
        field_verboses_post = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for value, expected in field_verboses_post.items():
            with self.subTest(value=value):
                self.assertEqual(
                    task_post._meta.get_field(value).verbose_name, expected
                )
        field_verboses_group = {
            'title': 'Название',
            'slug': 'Уникальный фрагмент URL',
            'description': 'Описание'
        }
        for value, expected in field_verboses_group.items():
            with self.subTest(value=value):
                self.assertEqual(
                    task_group._meta.get_field(value).verbose_name, expected
                )

    def test_help_text(self):
        task_post = PostModelTest.post
        task_group = PostModelTest.group
        field_help_text_post = {
            'text': 'Основной текст поста',
            'pub_date': 'Заполняется автоматически, в момент создания поста',
        }
        field_help_text_group = {
            'slug': 'Используется как стандарт записи ссылок на объект',
            'description': 'Опишите группу как можно подробнее',
            'title': 'Наименование группы, не более 200 символов',
        }

        for value, expected in field_help_text_post.items():
            with self.subTest(value=value):
                self.assertEqual(
                    task_post._meta.get_field(value).help_text, expected
                )
        for value, expected in field_help_text_group.items():
            with self.subTest(value=value):
                self.assertEqual(
                    task_group._meta.get_field(value).help_text, expected
                )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        task_post = PostModelTest.post
        string = 'author: {}, date: {:%m%d%Y}, group: {}, text: {}'
        expected_object_name_post = string.format(
            task_post.author,
            task_post.pub_date,
            task_post.group,
            task_post.text,
        )
        self.assertEqual(expected_object_name_post, str(task_post))
        task_group = PostModelTest.group
        expected_object_name_group = task_group.title
        self.assertEqual(expected_object_name_group, str(task_group))
