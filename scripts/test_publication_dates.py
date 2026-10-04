import unittest
from datetime import date
from publication_dates import crossref_date, latest_publications, format_date, valid_date


class PublicationDates(unittest.TestCase):
    def paper(self,key,value=None,image=None,year=2026,kind='journal'):
        return {'id':key,'year':year,'published_date':value,'image':image,'kind':kind}

    def test_online_date_wins_and_month_precision_is_preserved(self):
        fields=crossref_date({'published-online':{'date-parts':[[2025,12]]},'published':{'date-parts':[[2026,2,15]]}},'https://api.crossref.org/example')
        self.assertEqual(fields['published_date'],'2025-12')
        self.assertEqual(fields['published_date_basis'],'published-online')
        self.assertEqual(format_date(fields['published_date'],'ja'),'2025年12月')

    def test_indexing_date_is_not_a_publication_date(self):
        self.assertEqual(crossref_date({'created':{'date-parts':[[2026,1,2]]}},'https://example.org'),{})

    def test_latest_is_stable_with_partial_dates_and_missing_figures(self):
        papers=[self.paper('year'),self.paper('month','2026-08'),self.paper('day','2026-08-14'),self.paper('tie','2026-08-14',image={'path':'figure'}),self.paper('older','2025-12-31',year=2025)]
        self.assertEqual([p['id'] for p in latest_publications(papers,today=date(2026,10,4))],['day','tie','month','year','older'])

    def test_future_dates_excluded_and_preprints_included(self):
        papers=[self.paper('future','2026-11-01'),self.paper('preprint','2026-09-01',kind='preprint'),self.paper('other','2026-10-01',kind='other')]
        self.assertEqual([p['id'] for p in latest_publications(papers,today=date(2026,10,4))],['preprint'])

    def test_dates_never_gain_false_precision_in_any_language(self):
        for lang in ('en','zh','fr','ar','ja'):
            self.assertNotIn('14',format_date('2026-08',lang))
            self.assertIn('2026',format_date('2026',lang))
        self.assertFalse(valid_date('2026-02-30'))
        self.assertFalse(valid_date('2026-1'))


if __name__ == '__main__':
    unittest.main()
