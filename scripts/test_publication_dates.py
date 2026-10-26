import unittest
import copy
from datetime import date
from publication_dates import chronological_publications, crossref_date, latest_publications, format_date, valid_date


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

    def test_homepage_includes_missing_figures_and_pdfs_in_date_order(self):
        papers=[self.paper('no-figure','2026-10-01'),
                self.paper('first','2026-09-02',image={'path':'first.webp'}),
                self.paper('future','2026-11-01',image={'path':'future.webp'}),
                self.paper('preprint','2026-09-01',image={'path':'preprint.webp'},kind='preprint'),
                self.paper('older','2026-08-01',image={'path':'older.webp'})]
        self.assertEqual([p['id'] for p in latest_publications(papers,count=2,today=date(2026,10,4))],['no-figure','first'])
        self.assertEqual(len(papers),5)

    def test_homepage_uses_catalog_order_for_accepted_papers_without_pdfs(self):
        accepted=self.paper('accepted',image=None)
        accepted.update(status='accepted',event_start_date='2026-11-23',pdf=None)
        papers=[self.paper('published','2026-10-01'),accepted]
        snapshot=copy.deepcopy(papers)
        self.assertEqual([p['id'] for p in latest_publications(papers,today=date(2026,10,26))],
                         [p['id'] for p in chronological_publications(papers)])
        self.assertEqual(papers,snapshot)

    def test_full_catalog_retains_all_records_in_chronological_order(self):
        papers=[self.paper('undated'),self.paper('first','2026-08-14'),self.paper('same-day','2026-08-14'),self.paper('month','2026-08'),self.paper('other','2026-09-01',kind='other'),self.paper('online-before-issue','2025-12-01'),self.paper('older','2025-12-02',year=2025)]
        self.assertEqual([p['id'] for p in chronological_publications(papers)],['other','first','same-day','month','online-before-issue','undated','older'])
        self.assertEqual(len(chronological_publications(papers)),len(papers))

    def test_undated_accepted_papers_use_conference_dates_instead_of_addition_dates(self):
        first=self.paper('accepted-first');first.update(status='accepted',catalog_added_on='2026-08-01',event_start_date='2026-11-23')
        second=self.paper('accepted-second');second.update(status='accepted',catalog_added_on='2026-10-22',event_start_date='2026-11-16',expected_publication_month='2026-11')
        papers=[self.paper('published-september','2026-09'),first,second,self.paper('year-only')]
        snapshot=copy.deepcopy(papers)
        self.assertEqual([p['id'] for p in chronological_publications(papers)],
                         ['accepted-first','accepted-second','published-september','year-only'])
        self.assertEqual(papers,snapshot,'Catalog ordering must not invent publication dates')

    def test_known_publication_dates_take_priority_over_conference_and_addition_dates(self):
        accepted=self.paper('accepted-with-date','2026-07-01')
        accepted.update(status='accepted',catalog_added_on='2026-10-22',event_start_date='2026-11-23')
        papers=[accepted,self.paper('published-september','2026-09')]
        self.assertEqual([p['id'] for p in chronological_publications(papers)],
                         ['published-september','accepted-with-date'])

    def test_missing_conference_dates_can_fall_back_without_inventing_a_date(self):
        accepted=self.paper('accepted');accepted.update(status='accepted',catalog_added_on='2026-10-22',event_start_date='2026-99-99')
        no_date=self.paper('unknown-conference');no_date.update(status='accepted',expected_publication_month='2026-11')
        papers=[self.paper('published','2026-09'),accepted,no_date]
        self.assertEqual([p['id'] for p in chronological_publications(papers)],['accepted','published','unknown-conference'])

    def test_undated_imports_invalid_addition_dates_and_old_years_are_not_promoted(self):
        imported=self.paper('imported');imported['catalog_added_on']='2026-10-22'
        invalid=self.paper('invalid');invalid.update(status='accepted',catalog_added_on='2026-99-99')
        older=self.paper('older',year=2025);older.update(status='accepted',catalog_added_on='2026-10-22')
        papers=[imported,invalid,older,self.paper('published','2026-09')]
        self.assertEqual([p['id'] for p in chronological_publications(papers)],
                         ['published','imported','invalid','older'])

    def test_dates_never_gain_false_precision_in_any_language(self):
        for lang in ('en','zh','fr','ar','ja'):
            self.assertNotIn('14',format_date('2026-08',lang))
            self.assertIn('2026',format_date('2026',lang))
        self.assertFalse(valid_date('2026-02-30'))
        self.assertFalse(valid_date('2026-1'))


if __name__ == '__main__':
    unittest.main()
