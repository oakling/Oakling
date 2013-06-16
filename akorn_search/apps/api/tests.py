from django.test import TestCase
from django.test.client import RequestFactory

from apps.accounts.models import AkornUser
from .views import JSONResponseMixin, SavedSearchMixin

class JSONMixinTestCase(TestCase):
    example = {"fish": "horse"}
    expected = '{"fish": "horse"}'

    def setUp(self):
        self.obj = JSONResponseMixin()

    def test_json_encoding(self):
        out = self.obj.convert_context_to_json(self.example)
        self.assertJSONEqual(out, self.expected)

    def test_rendering(self):
        response = self.obj.render_to_response(self.example)
        self.assertContains(response, self.expected)
        self.assertEqual(response['Content-Type'], 'application/json')


class LoggedInSavedSearchMixinTestCase(TestCase):
    mock_searches = {"mock": "data"}

    def setUp(self):
        # Create a user without saved searches
        self.empty = AkornUser.objects.create_user('empty@fish.com', 'fish')
        # Create a user with saved searches
        self.full = AkornUser.objects.create_user('full@fish.com', 'fish')
        self.full.settings = self.mock_searches
        self.full.save()
        self.factory = RequestFactory()

    def test_getting_no_saved_searches(self):
        obj = SavedSearchMixin()
        # Create a meaningless test request instance
        request = self.factory.get('/test')
        # Add test user (is_authenticated will return true)
        request.user = self.empty
        # Set request on mixin instance
        obj.request = request
        # Get their saved searches
        searches, user = obj.get_saved_searches()
        # Should get an empty dict because this user has no saved searches
        self.assertEqual(searches, {})
        # Should also return the requesting user
        self.assertEqual(user, self.empty)

    def test_getting_saved_searches(self):
        obj = SavedSearchMixin()
        # Create a meaningless test request instance
        request = self.factory.get('/test')
        # Add test user (is_authenticated will return true)
        request.user = self.full
        # Set request on mixin instance
        obj.request = request
        # Get their saved searches
        searches, user = obj.get_saved_searches()
        # Should get mock dict
        self.assertEqual(searches, self.mock_searches)
        # Should also return the requesting user
        self.assertEqual(user, self.full)
