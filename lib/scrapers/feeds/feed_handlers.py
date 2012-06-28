import re

handlers = {
    "default": {
        "identifier": lambda item: 'doi:' + item['doi'],
        "url": lambda item: item['url'],
    },
    "aps_feed": {
        "identifier": lambda item: 'doi:' + item['prism_doi'],
        "url": lambda item: item['link'],
    },
    "acs_feed": {
        "identifier": None,
        "url": lambda item: item['feedburner_origlink'],
    },
    "iop_feed": {
        "identifier": None,
        "url": lambda item: item['link'],
    },
    "arxiv_feed": {
        "identifier": lambda item: "arxiv:" + arxiv_id(item['link']),
        "url": lambda item: item['link'],
    },
    "nature_feed": {
        "identifier": lambda item: "doi:" + item['prism_doi'],
        "url": lambda item: item['prism_url'],
    },
}

# helper functions for arxiv
def arxiv_id(url):
    return remove_vNumber(re.search('(?:abs|pdf)/(.*)', url).groups()[0])

def remove_vNumber(s):
    return re.sub(r'v[0-9]+', '', s)
