urls = [
    # American Chemical Society
    (r'acs.org', 'scrape_acs'),

    # IOP
    (r'iop.org', 'scrape_iop'),

    # National Academy of Sciences
    # American Society for Biochemistry and Molecular Biology
    (r'pnas.org', 'scrape_nas'),
    (r'jbc.org', 'scrape_nas'),
    (r'mcponline.org', 'scrape_nas'),
    (r'jlr.org', 'scrape_nas'),

    # APS
    (r'aps.org', 'scrape_pr'),

    # Science
    (r'sciencemag.org', 'scrape_science'),
]
