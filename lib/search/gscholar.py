import urllib
import urllib2
import lxml.html

def search(search_term, max_results=10):
    url = "http://scholar.google.com/scholar?"
    query_args = {'q': search_term,
                'num': max_results}
    encoded_args = urllib.urlencode(query_args)
   
    headers = {'User-Agent': 'Mozilla/5.0',}

    req = urllib2.Request(url + encoded_args, headers=headers)
    page = urllib2.urlopen(req)

    tree = lxml.html.parse(page, base_url=url)

    articles = []
 
    for result in tree.xpath(".//div[@class='gs_r']"):
        article = {}

        es_title = result.xpath(".//h3[@class='gs_rt']")

        try:
            article['title'] = es_title[0].text_content()
        except IndexError:
            pass

        try:
            article['uri'] = es_title[0].xpath('.//a')[0].attrib['href']
        except IndexError:
            pass

        es_authors = result.xpath(".//div[@class='gs_a']")

        if len(es_authors) != 0:
            authors_line = es_authors[0].text_content()
        sections = authors_line.replace(u'\u2026', '').split(' - ')
        authors = [author.strip() for author in sections[0].split(',') if len(author.strip()) != 0]

        article['authors'] = authors

        articles.append(article)
 
    return articles
