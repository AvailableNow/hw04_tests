from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from posts.models import Group, Post

User = get_user_model()


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='testauthor')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='testslug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованый клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_guest_url_exists_at_desired_location(self):
        """Проверка кодов ответа страниц неавторизованному пользователю."""
        guest_urls = [
            '/',
            '/group/testslug',
            '/profile/testauthor',
            f'/posts/{self.post.pk}/'
        ]
        for adress in guest_urls:
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress, follow=True)
                self.assertEqual(response.status_code, 200)

    def test_authorized_url_exists_at_desired_location(self):
        """Проверка кодов ответа страниц авторизованному пользователю."""
        authorized_url = [
            '/',
            '/group/testslug',
            '/profile/testauthor',
            f'/posts/{self.post.pk}/',
            f'/posts/{self.post.pk}/edit/',
            '/create/',
        ]
        for adress in authorized_url:
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress, follow=True)
                self.assertEqual(response.status_code, 200)

    def test_redirect_anonymous_on_admin_login(self):
        """Проверка редиректов для неавторизованных пользователей."""
        url_redirect_name = {
            '/auth/login/?next=/create/': '/create/',
            (f'/auth/login/?next=/posts/{self.post.pk}/edit/'):
            f'/posts/{self.post.pk}/edit/',
        }
        for address_redirect, address in url_redirect_name.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(response, address_redirect)

    def test_guest_url_correct_template(self):
        """URL-адрес использует корректный шаблон, для неавторизованного."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/testslug/': 'posts/group_list.html',
            '/profile/testauthor/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertTemplateUsed(response, template)

    def test_authorized_url_correct_template(self):
        """URL-адрес использует корректный шаблон, для авторизованного."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/testslug/': 'posts/group_list.html',
            '/profile/testauthor/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url, follow=True)
                self.assertTemplateUsed(response, template)

    def test_error(self):
        response = self.guest_client.get('/unexisting-page/')
        self.assertEqual(response.status_code, 404)
