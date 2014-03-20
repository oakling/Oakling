from datetime import datetime
import json
import mock

from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import reverse
from django.conf import settings
from django.test import TestCase, Client
from django.test.client import RequestFactory
from django.utils.importlib import import_module

from apps.accounts.models import AkornUser
from .views import JSONResponseMixin, SavedSearchMixin
import apps.api.views as views

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


# TODO Should probably be separate test cases
# TODO Missing tests for successfully removing searches from session
class DeleteSavedSearchView(TestCase):
    mock_data = {'test': {'fish': 'horse'}}

    def setUp(self):
        self.url = reverse('api:remove_search')
        # Create a user without saved searches
        self.empty = AkornUser.objects.create_user('empty@fish.com', 'fish')
        # Create a user with saved searches
        self.full = AkornUser.objects.create_user('full@fish.com', 'fish')
        self.full.settings = self.mock_data
        self.full.save()

    def test_no_query(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)

    def test_no_searches_anon(self):
        response = self.client.get(self.url, {'query_id': 'fake'})
        self.assertEqual(response.status_code, 404)

    def test_no_searches_user(self):
        self.client.login(email='empty@fish.com', password='fish')
        response = self.client.get(self.url, {'query_id': 'test'})
        self.assertEqual(response.status_code, 404)

    def test_success_user(self):
        self.client.login(email='full@fish.com', password='fish')
        response = self.client.get(self.url, {'query_id': 'test'})
        self.assertEqual(response.status_code, 204)
        # Get user from db
        user = AkornUser.objects.get(pk=self.full.pk)
        # Have only added one search, so this should be empty
        self.assertEqual(user.settings, {})

    def test_missing_search_user(self):
        self.client.login(email='full@fish.com', password='fish')
        response = self.client.get(self.url, {'query_id': 'not_there'})
        self.assertEqual(response.status_code, 400)


class MockJournalDocument(dict):
    id = None


class MockJournalAutoCompleteView(views.JournalAutoCompleteView):
    @classmethod
    def get_journal_docs(cls, db=None):
        journal = MockJournalDocument()
        journal.id = "f45f136fbd14caa156e5b4b8467e6521"
        journal["name"] = "Test"
        journal["sorted_aliases"] = [['test', 'Test']]

        journal2 = MockJournalDocument()
        journal2.id = "f45f136fbd14caa156e5b4b84611bba5"
        journal2["name"] = "House"
        journal2["sorted_aliases"] = [['fish', 'Fish']]

        return [journal, journal2]


class JournalsViewTestCase(TestCase):
    journal_out = {"text": "Test", "full": "Test", "id": "f45f136fbd14caa156e5b4b8467e6521", "type": "journal"}
    journal2_out = {"text": "Fish", "full": "House", "id": "f45f136fbd14caa156e5b4b84611bba5", "type": "journal"}

    def test_journals_returned(self):
        out = MockJournalAutoCompleteView.find_journals(None)
        self.assertEqual(out, [self.journal_out, self.journal2_out])

    def test_journals_partial(self):
        out = MockJournalAutoCompleteView.find_journals('te')
        self.assertEqual(out, [self.journal_out])

    def test_journals_none(self):
        out = MockJournalAutoCompleteView.find_journals('not')
        self.assertEqual(out, [])


class ArticlesViewSplitArgTestCase(TestCase):
    def test_lucene_split_args(self):
        args = "FishDogHorse"
        bits = views.ArticlesView.lucene_split_arg(args)
        self.assertEqual([args], bits)

    def test_lucene_multiple(self):
        delimiter = views.ArticlesView.delimiter
        args = delimiter.join(["Fish", "Dog", "Horse"])
        bits = views.ArticlesView.lucene_split_arg(args)
        self.assertEqual(["Fish", "Dog", "Horse"], bits)


class ArticlesViewKeywordTestCase(TestCase):
    def test_lucene_single_keyword_split(self):
        delimiter = views.ArticlesView.delimiter
        in_str = "Horse"
        out_bits = views.ArticlesView.lucene_split_keywords(in_str)
        self.assertEqual([["Horse"]], out_bits)

    def test_lucene_multiple_keyword_split(self):
        in_str = "Horse Donkey|Cat|Fish"
        out_bits = views.ArticlesView.lucene_split_keywords(in_str)
        self.assertEqual([["Horse", "Donkey"], ["Cat"], ["Fish"]], out_bits)

class ArticlesViewQueryTestCase(TestCase):
    def test_make_full_query(self):
        out = views.ArticlesView.lucene_get_query(keywords=[['Word', 'Horse'], ['Fish']],
            journals=['21412412', '1241525211'])
        expected = '((Word AND Horse) OR (Fish)) AND journalID:(21412412 OR 1241525211)'
        self.assertEqual(out, expected)

    def test_make_keyword_query(self):
        out = views.ArticlesView.lucene_get_query(keywords=[['Word'], ['Fish']])
        expected = '((Word) OR (Fish))'
        self.assertEqual(out, expected)

    def test_make_journal_query(self):
        out = views.ArticlesView.lucene_get_query(
            journals=['312452341', '211241412'])
        expected = "journalID:(312452341 OR 211241412)"
        self.assertEqual(out, expected)

    def test_single_keyword_query(self):
        out = views.ArticlesView.lucene_get_query(keywords=[['Horse']])
        self.assertEqual(out, '((Horse))')

    def test_single_journal_query(self):
        out = views.ArticlesView.lucene_get_query(journals=['Horse'])
        self.assertEqual(out, 'journalID:(Horse)')


class ArticlesViewLimitTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_no_limit(self):
        view = views.ArticlesView()
        view.request = self.factory.get('/api/articles')
        self.assertEqual(view.doc_limit, view.max_limit)

    def test_limit(self):
        view = views.ArticlesView()
        view.request = self.factory.get('/api/articles', {'limit': '10'})
        self.assertEqual(view.doc_limit, 10)

    def test_bad_limit(self):
        view = views.ArticlesView()
        view.request = self.factory.get('/api/articles', {'limit': 'fish'})
        self.assertRaises(views.BadRequest, getattr, view, 'doc_limit')


class ArticlesViewSkipTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_no_skip(self):
        view = views.ArticlesView()
        view.request = self.factory.get('/api/articles')
        self.assertEqual(view.doc_skip, None)

    def test_skip(self):
        view = views.ArticlesView()
        view.request = self.factory.get('/api/articles', {'skip': '10'})
        self.assertEqual(view.doc_skip, 10)

    def test_bad_skip(self):
        view = views.ArticlesView()
        view.request = self.factory.get('/api/articles', {'skip': "fish"})
        self.assertRaises(views.BadRequest, getattr, view, 'doc_skip')


class ArticlesViewProcessDocs(TestCase):
    all_doc = {
            '_id': 'some random id',
            'date_published': 1372274046.607653,
            'date_revised': 1372274070.96599,
            'date_received': 1372274197.663496,
            'date_scraped': 1352274180.663496
        }
    revised_doc = {
            '_id': 'another id',
            'date_revised': 1372274070.96599
        }
    scraped_doc = {
            '_id': 'a third id',
            'date_scraped': 1352274180.663496
        }
    nothing_doc = {
            '_id': 'a fourth id',
        }

    def test_all_doc(self):
        doc_date = views.ArticlesView.get_doc_date(self.all_doc)
        self.assertEqual(doc_date, datetime.fromtimestamp(1352274180.663496))

    def test_revised_doc(self):
        doc_date = views.ArticlesView.get_doc_date(self.revised_doc)
        self.assertEqual(doc_date, None)

    def test_received_doc(self):
        doc_date = views.ArticlesView.get_doc_date(self.scraped_doc)
        self.assertEqual(doc_date, datetime.fromtimestamp(1352274180.663496))

    def test_nothing_docs(self):
        doc_date = views.ArticlesView.get_doc_date(self.nothing_doc)
        self.assertEqual(doc_date, None)
