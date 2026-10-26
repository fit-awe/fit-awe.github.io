import unittest
from bs4 import BeautifulSoup
from build_content import latest_cards


class HomePublications(unittest.TestCase):
    def paper(self):
        return dict(id='accepted-no-pdf',year=2026,kind='conference',
                    title='A paper without a public PDF',authors=['Example Author'],
                    venue='ISS 2026',url='https://example.org/paper',image=None,pdf=None,
                    published_date=None,status='accepted',event_start_date='2026-11-23',
                    event_end_date='2026-11-26')

    def test_no_pdf_or_figure_keeps_a_working_card_and_accurate_status(self):
        paper=self.paper()
        card=BeautifulSoup(latest_cards([paper]),'html.parser').select_one('.latest-paper')
        self.assertEqual(card.select_one('.paper-title a')['href'],paper['url'])
        self.assertFalse(card.select('.paper-figure,img'))
        self.assertEqual(card.select_one('.paper-status').text,'Accepted')
        self.assertIn('Conference dates',card.select_one('.paper-date').text)
        self.assertEqual([t['datetime'] for t in card.select('time')],['2026-11-23','2026-11-26'])
        self.assertIsNone(paper['published_date'])

    def test_missing_date_preserves_year_only_precision(self):
        paper=self.paper()
        for field in ('status','event_start_date','event_end_date'):
            paper.pop(field)
        card=BeautifulSoup(latest_cards([paper]),'html.parser')
        self.assertEqual(card.time['datetime'],'2026')
        self.assertIsNone(card.select_one('.paper-status'))


if __name__=='__main__':
    unittest.main()
