# Load journal scrapers into our db
import couchdb

scrapers = {'pra.aps.org': ('lib.scrapers.journals.scrape_pr', 'Phys. Rev. A'),
            'prb.aps.org': ('lib.scrapers.journals.scrape_pr', 'Phys. Rev. B'),
            'prc.aps.org': ('lib.scrapers.journals.scrape_pr', 'Phys. Rev. C'),
            'prd.aps.org': ('lib.scrapers.journals.scrape_pr', 'Phys. Rev. D'),
            'pre.aps.org': ('lib.scrapers.journals.scrape_pr', 'Phys. Rev. E'),
            'prx.aps.org': ('lib.scrapers.journals.scrape_pr', 'Phys. Rev. X'),
            'prl.aps.org': ('lib.scrapers.journals.scrape_pr', 'Phys. Rev. Lett.'),
            'prst-ab.aps.org': ('lib.scrapers.journals.scrape_pr', 'Phys. Rev. ST Accel. Beams'),
            'prst-per.aps.org': ('lib.scrapers.journals.scrape_pr', 'Phys. Rev. ST Physics Ed. Research'),
		        'rmp.aps.org': ('lib.scrapers.journals.scrape_pr', 'Rev. Mod. Phys.'),
            'prola.aps.org': ('lib.scrapers.journals.scrape_pr', 'Phys. Rev.'),
            'iopscience.iop.org': ('lib.scrapers.journals.scrape_iop', None),
            'www.pnas.org': ('lib.scrapers.journals.scrape_nas', None),
            'www.sciencemag.org': ('lib.scrapers.journals.scrape_science', 'Science'),
            'pubs.acs.org': ('lib.scrapers.journals.scrape_acs', None),
            'arxiv.org': ('lib.scrapers.journals.scrape_arxiv', None),}

db = couchdb.Server()['scrapers']

for domain, (module, journal) in scrapers.items():
  records = db.view('index/domain', key=domain, include_docs=True).rows
  if not records:
    print "Adding %s -> %s" % (domain, module)
    doc = {'module': module,
           'domain': domain,
           'journal': journal,}
    db.save(doc)
  else:
    print "%s already in db" % domain
    
    doc = records[0].doc
    doc['module'] = module
    db.save(doc)
