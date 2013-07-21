from django import forms

example_config = """<?xml version=\"1.0\"?>
<scraper>
    <journal>
        <title type=\"metaTag\" value=\"\" />
        <date_published type=\"metaTag\" value=\"\" />
        <author_names type=\"metaList\" value=\"\" />
        <journal type=\"metaTag\" value=\"\" />
        <abstract type=\"css\" value=\"\" />
    </journal>
</scraper>"""

class SimulatorForm(forms.Form):
    scraper_config = forms.CharField(widget=forms.Textarea, initial=example_config)
    article_url = forms.URLField()
