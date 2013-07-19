from django import forms

class SimulatorForm(forms.Form):
    scraper_config = forms.CharField(widget=forms.Textarea)
    article_url = forms.URLField()
