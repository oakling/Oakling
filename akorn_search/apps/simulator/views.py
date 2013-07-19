import lxml

from django.http import HttpResponse
from django.views.generic import FormView
from django import forms

from .forms import SimulatorForm

from akorn.scrapers.base import BaseScraper

class SimulatedScraper(BaseScraper):
    def __init__(self, config_xml_str):
        """
        Overload BaseScraper.__init__, to load config from param not file
        """
        self.config_data = lxml.etree.fromstring(config_xml_str)

class SimulatorView(FormView):
    template_name = 'simulator/simulator.html'
    form_class = SimulatorForm

    def simulate_scrape(self, url, config):
        """
        Return dict of scraped article
        """
        # Instantiate the scraper with the supplied configuration
        scraper = SimulatedScraper(config)
        # Scrape the given url
        return scraper.scrape_article(url)

    def form_valid(self, form):
        """
        Return template rendered with scraped content or error
        """
        # Add the supplied form into the context
        context = {'form': form}
        # Find the form inputs
        url = form.cleaned_data['article_url']
        config = form.cleaned_data['scraper_config']
        try:
            # Use the supplied  config to scrape the given url
            context['scraped'] = self.simulate_scrape(url, config)
        except Exception as e:
            # Catch errors and pas to context
            context['error'] = str(e)
        # Render the original template with the new context
        return self.render_to_response(context)
