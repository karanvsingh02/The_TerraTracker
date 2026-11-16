import unittest
from backend.services.places import search_places

class PlaceSearchTests(unittest.TestCase):
    def test_country_and_region_disambiguate(self):
        places=search_places('London, Ontario')
        self.assertTrue(places)
        self.assertIn('Canada',places[0]['label'])
        self.assertAlmostEqual(places[0]['lat'],43,delta=1)

    def test_accents_case_and_empty_queries(self):
        self.assertEqual(search_places(''),[])
        self.assertEqual(search_places('x'),[])
        self.assertEqual(search_places('MONTRÉAL'),search_places('montreal'))
        self.assertTrue(search_places('montreal'))
        self.assertLessEqual(len(search_places('san')),10)
        self.assertEqual(search_places('zzzz-unlisted-location'),[])
