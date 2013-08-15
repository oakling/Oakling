import functools
import lxml

from django.http import HttpResponse
from django.views.generic import FormView
from django import forms

from .forms import SimulatorForm

import akorn.scrapers.base as base
import akorn.scrapers.utils as utils


class SimulatedConfig(base.Config):
    def __init__(self, config_str):
        parsed = self.parse_config(config_str)
        compiled_config = self.compile_config(parsed)
        # Place the config where it needs to be
        self.config = compiled_config


class SimulatedScraper(base.BaseScraper):
    def __init__(self, config_str):
        """
        Overload BaseScraper.__init__, to load config from param not file
        """
        self.config = SimulatedConfig(config_str)

    def valid(self, data):
        missing = []
        # Curry check_value with container for missing properties
        curried_check = functools.partial(self.check_value, missing=missing)
        # Walk over the acquired data to check a value is set for each property
        utils.walk_and_apply(data, curried_check)
        # Set the list of missing properties as instance variable
        self.missing = missing
        return missing


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
        return scraper.scrape_article(url), scraper

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
            # Use the supplied config to scrape the given url
            context['scraped'], scraper = self.simulate_scrape(url, config)
            context['out_missing'] = scraper.missing
            context['config'] = scraper.config
        except Exception as e:
            # Catch other errors and pass to context
            context['out_error'] = str(e)
        # Render the original template with the new context
        return self.render_to_response(context)
