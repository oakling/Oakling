import sys
import urllib2
import re
import lxml.html
import urlparse
import utils
import datetime
import time

# Scaper metadata
SCRAPER_DOMAINS = ['pra.aps.org',
                   'prb.aps.org',
                   'prc.aps.org',
                   'prd.aps.org',
                   'pre.aps.org',
                   'prx.aps.org',
                   'prl.aps.org',
                   'prst-ab.aps.org',
                   'prst-per.aps.org',
                   'rmp.aps.org',
                   'prola.aps.org',
                   'link.aps.org',]

# The browser identity we'll assume for this run. Possibly not needed.
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',} 

# Map of journal domains to the actual journal (pra.aps.org -> Phys. Rev. A)
# This will probably live in the actual scraper invoker API eventually.
journal_domains = {'pra': 'Phys. Rev. A', 
                   'prb': 'Phys. Rev. B', 
                   'prc': 'Phys. Rev. C', 
                   'prd': 'Phys. Rev. D', 
                   'pre': 'Phys. Rev. E', 
                   'prx': 'Phys. Rev. X', 
                   'prl': 'Phys. Rev. Lett.', 
                   'prst-ab': 'Phys. Rev. ST Accel. Beams', 
                   'prst-per': 'Phys. Rev. ST Physics Ed. Research', 
		               'rmp': 'Rev. Mod. Phys.',
                   'prola': 'Phys. Rev.',}

# Use the previous map to work out what the current journal is. Again
# will probably live elsewhere, since the scraper doesn't need to know
# what journal it's scraping, we can add that info after running it.

def recognise_journal(abstract_url):
  url_parsed = urlparse.urlparse(abstract_url)
  first = url_parsed.netloc.split('.')[0]

  return journal_domains[first]

def parse_citation(citation):
  # Phys. Rev. B 74, 195118 (2006)
  journal, volume, page, year = re.findall(r"(.*?) ([0-9]+), ([0-9\(\)A-Z]+) \(([0-9]+)\)", citation)[0]
  return {'journal': journal,
          'volume': int(volume),
          'page': page,
          'year': int(year),}
 
# Scrape the given url
def scrape(abstract_url):
  req = urllib2.Request(abstract_url, headers=headers)
  urls, page = utils.get_response_chain(req)

  # Parse the HTML into a tree we can query
  page_text = page.read().decode('utf-8')
  tree = lxml.html.fromstring(page_text, base_url=abstract_url)

  print page_text

  # Make XPATH queries for the first H1 and second H2 for the article title and how to cite it
  title = tree.xpath('//h1')[0].text_content().strip()
  cite_as = tree.xpath('//h2')[1].text.strip()

  # Scrub the citation.
  cite_as = re.sub('\s{1,}', ' ', cite_as)
  cite_as = re.sub(' \[.*?\]', '', cite_as)

  # Make our article object
  article = {}
  article['scraper'] = 'pr'
  article['title'] = title
  article['cite'] = cite_as
  
  try:
    article['citation'] = parse_citation(cite_as)
  except:
    pass

  # Grab all links inside the the <div> with the id='aps-authors' and take their text as the author list.
  article['author_names'] = [author.text.strip() for author in tree.xpath("//div[@id='aps-authors']//a")]

  try:
    article['author_names'].remove('Hide All Authors/Affiliations')
  except:
    pass

  # Find the div with class 'aps-abstractbox' and grab the text of the first <p> within it as the abstract
  try:
    article['abstract'] = tree.xpath("//div[@class='aps-abstractbox']/p")[0].text_content()
  except:
    pass

  months = {'January':1, 'February':2, 'March':3, 'April':4, 'May':5, 'June':6, 'July':7, 'August':8, 'September':9, 'October':10, 'November':11, 'December':12}

  # Received 21 December 2011; revised 18 February 2012; published  9 April 2012

  date_received = re.findall('Received\s+([0-9]+)\s+([A-Za-z]+)\s+([0-9]+)', page_text)
  date_revised = re.findall('revised\s+([0-9]+)\s+([A-Za-z]+)\s+([0-9]+)', page_text) 
  date_published = re.findall('published\s+([0-9]+)\s+([A-Za-z]+)\s+([0-9]+)', page_text) 

  def make_datestamp(date_tuple):
    year = int(date_tuple[2])
    month = months[date_tuple[1]]
    day = int(date_tuple[0])
    return time.mktime(datetime.date(year, month, day).timetuple())

  if date_received:
    article['date_received'] = make_datestamp(date_received[0])
  if date_revised:
    article['date_revised'] = make_datestamp(date_revised[0])
  if date_published:
    article['date_published'] = make_datestamp(date_published[0])

  # Find the <div> with the id 'aps-article-info' and take the respective columns cell contents as the type of id and id.
  article['ids'] = dict(zip([e.text.strip().lower().replace(':','') for e in tree.xpath("//div[@id='aps-article-info']//div[@class='table-cell bold']")],\
                            [e.text.strip() for e in tree.xpath("//div[@id='aps-article-info']//div[@class='table-cell']")]))

  if 'subject areas' in article['ids']:
    article['pr_subject_areas'] = article['ids']['subject areas']
    del article['ids']['subject areas']

  article['journal'] = recognise_journal(page.geturl())
  article['source_urls'] = [uri for _, uri in urls]

  # PACS will be recognised as an id, even though its actually a list of categories.
  # Split them out into their own custom field and delete from ids.
  if 'pacs' in article['ids']:
    article['categories'] = {'PACS':[c.strip() for c in
                                     article['ids']['pacs'].split(',')]}
    del article['ids']['pacs']

  
  return article

if __name__ == "__main__":
  print scrape(sys.argv[1])
