handlers = {
    "default": {
        "identifier": lambda item: 'doi:' + item['doi'],
        "url": lambda item: item['url'],
    },
    "aps_feed": {
        "identifier": lambda item: 'doi:' + item['prism_doi'],
        "url": lambda item: item['link'],
    },
    "iop_feed": {
        "identifier": None,
        "url": lambda item: item['link'],
    },
}
