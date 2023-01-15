from django.test import TestCase
from django.urls import reverse

USERNAME = 'test_user'
SLUG = 'test_group'
POST_ID = 1


class RoutesTest(TestCase):
    def test_routes(self):

        TEST_URLS = [
            ('index', '/'),
            ('post_create', '/create/'),
            ('group_list', SLUG, f'/group/{SLUG}/'),
            ('profile', USERNAME, f'/profile/{USERNAME}/'),
            ('post_detail',
                POST_ID, f'/posts/{POST_ID}/'),
            ('post_edit',
                POST_ID, f'/posts/{POST_ID}/edit/'),
        ]
        for document, *key, address in TEST_URLS:
            with self.subTest(document=document):
                self.assertEqual(reverse(
                    f'posts:{document}', args=key), address)
