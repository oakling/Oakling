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
    feed_url = forms.URLField(initial="http://", label="Feed URL")
    article_tag = forms.CharField(initial="link", help_text="The tag that contains the article URL in each feed item")
