import json

from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import reverse
from django.conf import settings
from django.test import TestCase, Client
from django.test.client import RequestFactory
from django.utils.importlib import import_module

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

    def test_saving_searches(self):
        obj = SavedSearchMixin()
        obj.set_saved_searches(self.mock_searches, self.empty)
        # Get the user again
        modified_user = AkornUser.objects.get(pk=self.empty.pk)
        self.assertEqual(modified_user.settings, self.mock_searches)

# TODO Should this be split up into separate TestCases?
class AnonSavedSearchMixinTestCase(TestCase):
    mock_searches = {"mock": "data"}

    def setUp(self):
        """
        Got session setup from http://stackoverflow.com/a/7722483/2196754
        """
        self.factory = RequestFactory()

        engine = import_module('django.contrib.sessions.backends.file')
        # Instantiate session for testing empty session
        empty = engine.SessionStore()
        empty.save()
        self.empty_session = empty
        # Instantiate 2nd session for user with existing session data
        filled = engine.SessionStore()
        filled.save()
        self.filled_session = filled
        self.filled_session['saved_searches'] = self.mock_searches
        self.filled_session.save()

    def test_getting_no_saved_searches(self):
        obj = SavedSearchMixin()
        # Set meaningless request on mixin instance
        request = self.factory.get('/test')
        # Set request properties to mimic no-logged in, without session
        request.user = AnonymousUser()
        request.session = self.empty_session
        # Set request on mixin instance
        obj.request = request
        # Get saved searches
        searches, user = obj.get_saved_searches()
        # No session saved searches should be found
        self.assertEqual(searches, {})
        # If session data is used then user should be None
        self.assertEqual(user, None)

    def test_getting_saved_searches(self):
        obj = SavedSearchMixin()
        # Set meaningless request on mixin instance
        request = self.factory.get('/test')
        # Set request properties to mimic no-logged in, with session data
        request.user = AnonymousUser()
        request.session = self.filled_session
        # Set request on mixin instance
        obj.request = request
        # Get saved searches
        searches, user = obj.get_saved_searches()
        # No session saved searches should be found
        self.assertEqual(searches, self.mock_searches)
        # If session data is used then user should be None
        self.assertEqual(user, None)

    def test_saving_searches(self):
        obj = SavedSearchMixin()
        # Set meaningless request on mixin instance
        request = self.factory.get('/test')
        # Set request properties to mimic no one logged in, with empty session
        request.user = AnonymousUser()
        request.session = self.empty_session
        # Set request on mixin instance
        obj.request = request
        obj.set_saved_searches(self.mock_searches, None)
        # Get the user again
        self.assertEqual(request.session['saved_searches'],
            self.mock_searches)


class SavedSearchViewTestCase(TestCase):
    mock_searches = '{"mock": "data"}'
    mock_json = {"mock": "data"}

    def setUp(self):
        self.url = reverse('api:save_search')

    def test_no_query(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)

    def test_non_logged_in(self):
        response = self.client.post(self.url, {'query': self.mock_searches})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        # Get the returned query id
        query_id = json.loads(response.content)['query_id']
        # Check session for right data associated with query id
        self.assertEqual(self.client.session['saved_searches'][query_id], self.mock_json)


class DeleteSavedSearchView(TestCase):
    def setUp(self):
        self.url = reverse('api:remove_search')

    def test_no_query(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)

    def test_no_searches(self):
        response = self.client.get(self.url, {'query_id': 'fake'})
        self.assertEqual(response.status_code, 404)
