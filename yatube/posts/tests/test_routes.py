from django.test import TestCase
from django.urls import reverse

USERNAME = 'test_user'
SLUG = 'test_group'
POST_ID = 1

INDEX = reverse('posts:index')
POST_CREATE = reverse('posts:post_create')
GROUP_LIST = reverse('posts:group_list', args=[SLUG])
PROFILE = reverse('posts:profile', args=[USERNAME])
POST_DETAIL = reverse('posts:post_detail', args=[POST_ID])
POST_EDIT = reverse('posts:post_edit', args=[POST_ID])


class RoutesTest(TestCase):
    def test_routes(self):

        test_urls = {
            INDEX: '/',
            POST_CREATE: '/create/',
            GROUP_LIST: f'/group/{SLUG}/',
            PROFILE: f'/profile/{USERNAME}/',
            POST_DETAIL: f'/posts/{POST_ID}/',
            POST_EDIT: f'/posts/{POST_ID}/edit/',
        }
        for page, url in test_urls.items():
            with self.subTest(page=page):
                self.assertEqual(page, url)
