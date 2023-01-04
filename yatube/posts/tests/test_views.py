from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from django import forms

from posts.models import Group, Post

User = get_user_model()


class GroupPostTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='testauthor')
        cls.group = Group.objects.create(
            title='Тестовая группа 1',
            slug='testslug_1',
            description='Тестовое описание 1',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый текст',
            # image=uploaded,
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованый клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_use_correct_templates(self):
        """URL-адрес использует корректный шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': f'{self.group.slug}'}):
            'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}):
            'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': f'{self.post.id}'}):
            'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': f'{self.post.id}'}):
            'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_group_0 = first_object.group.title
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0, self.user.username)
        self.assertEqual(post_group_0, self.group.title)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        expected = list(Post.objects.filter(
            group_id=self.group.id)[:settings.MAX_POSTS])
        self.assertEqual(list(response.context['page_obj']), expected)

    def test_profile_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.post.author})
        )
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        self.assertEqual(
            response.context['author'].username,
            self.user.username
        )
        self.assertEqual(post_text_0, self.post.text)

    def test_post_detail_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(response.context.get('post').text, self.post.text)
        self.assertEqual(response.context.get('post').author, self.post.author)
        self.assertEqual(response.context.get('post').group, self.post.group)

    def test_create_post_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_check_group_in_pages(self):
        """Проверяем появление поста на / главной странице сайта /
        странице выбранной группы,/ в профайле пользователя
        / с выбранной группой"""
        form_fields = {
            reverse("posts:index"): Post.objects.get(
                group=self.post.group
            ),
            reverse(
                "posts:group_list", kwargs={"slug": self.group.slug}
            ): Post.objects.get(group=self.post.group),
            reverse(
                'posts:profile', kwargs={'username': self.post.author}
            ): Post.objects.get(group=self.post.group),
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                form_field = response.context['page_obj']
                self.assertIn(expected, form_field)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.PAGE_NUBMER = 13
        cls.user = User.objects.create_user(username="NoName")
        cls.group = Group.objects.create(
            title='Тестовая группа 2',
            slug='testslug_2',
            description='Тестовое описание 2',
        )
        cls.post = Post.objects.bulk_create(
            [
                Post(
                    text=f"Тестовый текст{i}",
                    author=cls.user,
                    group=cls.group
                )
                for i in range(cls.PAGE_NUBMER)
            ]
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()

    def test_first_page_contains_ten_records(self):
        NUMBER_POSTS = 10
        templates_pages_names = {
            "posts/index.html": reverse("posts:index"),
            "posts/group_list.html": reverse(
                "posts:group_list", kwargs={"slug": self.group.slug}
            ),
            "posts/profile.html": reverse(
                "posts:profile", kwargs={"username": self.user.username}
            ),
        }
        for reverse_name in templates_pages_names.values():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(len(response.context["page_obj"]),
                                 NUMBER_POSTS
                                 )

    def test_second_page_contains_three_records(self):
        NUMBER_POSTS = 3
        templates_pages_names = {
            "posts/index.html": reverse("posts:index") + "?page=2",
            "posts/group_list.html": reverse(
                "posts:group_list", kwargs={"slug": "testslug_2"}
            )
            + "?page=2",
            "posts/profile.html": reverse(
                "posts:profile", kwargs={"username": "NoName"}
            )
            + "?page=2",
        }
        for reverse_name in templates_pages_names.values():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(len(response.context["page_obj"]),
                                 NUMBER_POSTS
                                 ),
