import feedparser
import functools
import lxml
import random

from django.core.mail import mail_managers
from django.http import HttpResponse
from django.views.generic import FormView
from django.template.loader import render_to_string
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

    def scrape_feed(self, feed_url, url_key='link'):
        """
        Return list of article URLS to scrape
        """
        items = feedparser.parse(feed_url).get('items')
        if not items:
            raise Exception("Failed to scrape feed")

        article_urls = [item.get(url_key) for item in items if url_key in item]

        if not article_urls:
            raise Exception("Failed to find URLs in feed. Try one of: {}.".format(', '.join(item.keys())))

        return article_urls

    def scrape_article(self, url, scraper):
        article = {}
        try:
            # Record the URL we're attempting to scrape
            article['url'] = url
            # Use the supplied config to scrape the given url
            article['scraped'], scraper = self.simulate_scrape(url, scraper)
            article['out_missing'] = scraper.missing
            article['config'] = scraper.config
        except Exception as e:
            # Catch other errors and pass to context
            article['out_error'] = str(e)
        return article

    def simulate_scrape(self, url, scraper):
        """
        Return dict of scraped article
        """
        # Scrape the given url
        return scraper.scrape_article(url), scraper

    def email_config(self, form):
        # Then email the config and feed definition to Managers
        mail_managers('Scraper request',
            render_to_string('simulator/email.txt',
                {'data': form.cleaned_data, 'user': self.request.user}))

    def run_config(self, form, context):
        # Add the supplied form into the context
        try:
            # Find the form inputs
            feed_url = form.cleaned_data['feed_url']
            url_key = form.cleaned_data['article_tag']
            config = form.cleaned_data['scraper_config']
            # Parse the feed and find the article urls
            articles = self.scrape_feed(feed_url, url_key)
            # Instantiate the scraper with the supplied configuration
            scraper = SimulatedScraper(config)
            # Grab any 2 articles
            articles = random.sample(articles, 2)
            # Try to scrape the selected articles
            context['articles'] = [self.scrape_article(url, scraper) for url in articles]
        except KeyError as e:
            context['error'] = 'All fields are required'
        except Exception as e:
            context['error'] = str(e)
        return context

    def form_valid(self, form):
        """
        Return template rendered with scraped content or error
        """
        context = {'form': form}

        # If the user pressed the Save button, rather than run
        if self.request.POST.get('save'):
            self.email_config(form)
        else:
            context = self.run_config(form, context)

        # Render the original template with the new context
        return self.render_to_response(context)
