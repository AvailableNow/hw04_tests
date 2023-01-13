from django.test import TestCase
from django.urls import reverse

USERNAME = 'test_user'
SLUG = 'test_group'
POST_ID = 1


class RoutesTest(TestCase):
    def test_routes(self):

        test_urls = [
            ['index', '/'],
            ['post_create', '/create/'],
            ['group_list', SLUG, f'/group/{SLUG}/'],
            ['profile', USERNAME, f'/profile/{USERNAME}/'],
            ['post_detail',
                POST_ID, f'/posts/{POST_ID}/'],
            ['post_edit',
                POST_ID, f'/posts/{POST_ID}/edit/'],
        ]
        for page, *var, url in test_urls:
            with self.subTest(page=page):
                self.assertEqual(reverse(f'posts:{page}', args=var), url)
