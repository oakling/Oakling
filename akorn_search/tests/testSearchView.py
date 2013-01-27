from django.test import TestCase

class SearchViewTestCase(TestCase):

    def test_view(self):
        response = self.client.get('/search/')
        assert response.status_code == 200
        assert response.templates[0].name == 'search/home.html'
        assert response.templates[1].name == 'page.html'
        assert 'AKORN' in response.content

