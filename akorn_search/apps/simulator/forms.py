from django import forms

example_config = """{
    \"title\": [
        {\"type\": \"metaTag\", \"value\": \"dc.title\"}
        ],
    \"date_published\": [
        {\"type\": \"metaTag\", \"value\": \"dc.date\"}
        ],
    \"author_names\": [
        {\"type\": \"metaList\", \"value\": \"dc.contributor\"}
        ],
    \"journal\": [
        {\"type\": \"metaTag\", \"value\": \"citation_journal_title\"}
        ],
    \"abstract\": [
        {\"type\": \"css\", \"value\": \"div.section p\", \"single\": true}
        ],
    \"publisher\": [
        {\"type\": \"metaTag\", \"value\": \"dc.publisher\"}
        ],
    \"doi\": [
        {\"type\": \"metaTag\", \"value\": \"citation_doi\"}
        ]
}"""

class SimulatorForm(forms.Form):
    scraper_config = forms.CharField(widget=forms.Textarea, initial=example_config)
    article_url = forms.URLField()
