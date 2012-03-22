import unittest

import scrape_pr, scrape_iop, scrape_nas, scrape_science, scrape_acs, scrape_arxiv
import test_data

class TestPhysRev(unittest.TestCase):
  def test_pra(self):
    article = scrape_pr.scrape('http://pra.aps.org/abstract/PRA/v85/i1/e010102')

    self.assertEqual(article, test_data.pra_1)

  def test_prb(self):
    article = scrape_pr.scrape('http://prb.aps.org/abstract/PRB/v85/i11/e115303')

    self.assertEqual(article, test_data.prb_1)

class TestIOP(unittest.TestCase):
  def test_iop1(self):
    article = scrape_iop.scrape('http://iopscience.iop.org/1748-0221/7/03/C03017')

    self.assertEqual(article, test_data.iop_1)

class TestNAS(unittest.TestCase):
  def test_pnas(self):
    article = scrape_nas.scrape('http://www.pnas.org/content/109/10/E588.abstract')

    self.assertEqual(article, test_data.pnas_1)

class TestScience(unittest.TestCase):
  def test_science(self):
    article = scrape_science.scrape('http://www.sciencemag.org/content/335/6073/1184')

    self.assertEqual(article, test_data.science_1)

class TestACS(unittest.TestCase):
  def test_molpharm(self):
    article = scrape_acs.scrape('http://pubs.acs.org/doi/abs/10.1021/mp200447r')

    self.assertEqual(article, test_data.acs_1)

class TestArxiv(unittest.TestCase):
  def test_arxiv1(self):
    article = scrape_arxiv.scrape('http://arxiv.org/abs/1203.1816')

    self.assertEqual(article, test_data.arxiv_1)

if __name__ == '__main__':
    unittest.main()
