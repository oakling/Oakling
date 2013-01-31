import sys
from lib.scrapers.journals.utils import get_tree, make_blank_article, get_meta, get_meta_list, make_datestamp
import time
from dateutil.parser import parse as parse_date

#TODO bepress

NECESSARY_FIELDS = ['title','author_names', 'journal']

title = ['citation_title', 'eprints.title', 'bepress_citation_title',
         'prism.title', 'DC.title', 'DC.Title', 'dc.title', 'dc.Title']

authors = ['citation_author', 'DC.creator', 'DC.Creator', 'dc.creator',
           'dc.Creator']

# when does this appear
contributors = ['DC.contributor', 'DC.Contributor', 'dc.contributor',
                'dc.Contributor']
#need to split this on semicolons?
authors_list = ['citation_authors']

abstract = ['DC.description.abstract', 'DC.Description.abstract',
            'dc.descrption.abstract', 'dc.Description.absract',
            'DC.description', 'DC.Description', 'dc.description',
            'dc.Description', 'description', 'Description']
publication_date = ['citation_publication_date', 'citation_dat', 'DC.issued',
                    'DC.Issued', 'dc.issued', 'dc.Issued', 'DC.date', 
                    'DC.Date', 'dc.date', 'dc.Date']
journal = ['citation_journal_title', 'DC.relation.ispartof',
           'dc.relation.ispartof']
publisher = ['citation_publisher', 'citation_dissertation_institution',
             'citation_technical_report_institution', 'DC.publisher',
             'DC.Publisher', 'dc.publisher', 'dc.Publisher']
volume = ['citation_volume', 'DC.citation.volume', 'dc.citation.volume']
issue = ['citation_issue', 'DC.citation.issue', 'dc.citation.issue']
firstpage = ['citation_firstpage', 'DC.citation.spage', 'dc.citation.spage']
lastpage = ['citation_lastpage', 'DC.citation.epage', 'dc.citation.epage']
issn = ['citation_issn']
isbn = ['citation_isbn']
keywords = ['citation_keywords', 'DC.subject', 'DC.Subject', 'dc.subject',
            'dc.Subject', 'keywords', 'Keywords']
language = ['citation_language', 'DC.language', 'DC.Language', 'dc.language',
            'dc.Language']
# Need to check for doi: scheme (eliminate http: results)
doi = ['citation_doi', 'DC.identifier', 'DC.Identifier', 'dc.identifier',
       'dc.Identifier']

def missingfields(article, necessaryfields):
    missing = []
    for field in necessaryfields:
        if field not in article or not article[field]:
            missing.append(field)
    return missing


def get_meta_list(names, tree):
    for name in names:
        attributes = tree.xpath("//meta[@name='%s']/@content" % name)
        if attributes:
            return attributes

def get_meta(names, tree):
    attributes = get_meta_list(names, tree)
    if attributes:
        return attributes[0]

def scrape_tree(tree, urls, page_text):

    article = {}
    article['source_urls'] = [uri for _, uri in urls]
    article['scraper'] = 'default'

    article['title'] = get_meta(title, tree)
    article['author_names'] = get_meta_list(authors, tree)

    if article['author_names'] is None:
      article['author_names'] = get_meta(authors_list, tree).split(';')

    article['abstract'] = get_meta(abstract, tree)
    
    article_doi = get_meta(doi, tree)
    if article_doi:
        article_doi = article_doi.replace('http://dx.doi.org/','')
    article['ids'] = {'doi': article_doi}

    article['journal'] = get_meta(journal, tree)
    article['publisher'] = get_meta(publisher, tree)

    article['citation'] = {}
    article['citation']['journal'] = article['journal']
    article['citation']['volume'] = get_meta(volume, tree)
    article['citation']['page_first'] = get_meta(firstpage, tree)
    article['citation']['page_last'] = get_meta(lastpage, tree)

    article['keywords'] = get_meta(keywords, tree)
    date = get_meta(publication_date, tree)
    if date:
        date = parse_date(date)
        article['date_published'] = time.mktime(date.timetuple())
        article['citation']['year'] = date.year

    return article

def scrape(abstract_url):
  tree, urls, page_text = get_tree(abstract_url) 

  article = scrape_tree(tree, urls, page_text)

  for field in NECESSARY_FIELDS:
        if field not in article or not article[field]:
            print field
            raise ScraperNotFound

  return article

if __name__ == "__main__":
  print scrape(sys.argv[1])
