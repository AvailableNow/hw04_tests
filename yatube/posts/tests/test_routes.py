from django.test import TestCase
from django.urls import reverse

from ..models import Group, Post, User


class RoutesTest(TestCase):
    def test_routes(self):
        user = User.objects.create_user(username='test_user')
        group = Group.objects.create(
            title='Наименование_группы',
            description='Описание_группы',
            slug='test_group'
        )
        post = Post.objects.create(
            text='публикация тестовая',
            group=group,
            author=user
        )

        test_urls = {
            reverse('posts:index'): '/',
            reverse('posts:post_create'): '/create/',
            reverse('posts:group_list',
                    args=[group.slug]): f'/group/{group.slug}/',
            reverse('posts:profile',
                    args=[user.username]): f'/profile/{user.username}/',
            reverse('posts:post_detail',
                    args=[post.id]): f'/posts/{post.id}/',
            reverse('posts:post_edit',
                    args=[post.id]): f'/posts/{post.id}/edit/',
        }
        for page, url in test_urls.items():
            self.assertEqual(page, url)
